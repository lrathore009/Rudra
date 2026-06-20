"""Phase 2 — Rudra single-voice orchestrator.

One persona (Rudra) talks to the owner. Internally it routes to the best of nine
subordinate specialists, enriches from that domain's data (bounded), and synthesizes a
single Rudra reply. The owner never sees a sub-agent name, intro, or routing preamble.
"""

from __future__ import annotations

import asyncio

from rudra.agents.base import (
    AGENT_REGISTRY,
    OPERATING_PRINCIPLES,
    AgentContext,
    AgentResponse,
    BaseAgent,
    RoutingCandidate,
    _heuristic_routing,
)
from rudra.agents.context_builder import AgentContextBuilder
from rudra.agents.types import AgentType
from rudra.brain.orchestrator import Brain, Message
from rudra.core.config import get_settings
from rudra.core.logging import get_logger
from rudra.memory.service import MemoryService

logger = get_logger(__name__)

RUDRA_PERSONA = """You ARE Rudra — the owner's single private intelligence, in the tradition of J.A.R.V.I.S.
You silently draw on internal departments (executive, research, concierge, travel, knowledge,
writing, presentation, operations, market intelligence) and the owner's own data, but you
ALWAYS speak as ONE assistant: Rudra.

- Discreet, capable, concise, executive-grade. No preamble, no self-introduction, no fluff.
- NEVER say "As your Research Analyst…", never name a department, specialist, or routing decision.
- Refer to the owner's data naturally ("your calendar shows…", "from your research library…"),
  never as a separate persona.
- Prefer structured, actionable output. Ground claims in the Intelligence provided; flag gaps.
"""

# One consistent voice for TTS — Rudra, not a per-specialist timbre.
RUDRA_VOICE: dict = {"pitch": 1.0, "rate": 1.03, "voice_hints": ["male", "calm", "british", "assistant"]}


class RudraCommandService:
    """Routes silently, enriches (bounded), and synthesizes one Rudra reply."""

    def __init__(self, brain: Brain | None = None):
        self.brain = brain or Brain()
        self.budget = get_settings().stream_enrich_budget_seconds

    # ---- routing (silent) ----------------------------------------------------
    def classify_fast(self, query: str) -> tuple[AgentType, list[RoutingCandidate]]:
        """Instant heuristic routing — no LLM hop (used by the streaming path)."""
        candidates = _heuristic_routing(query)
        return candidates[0].agent_type, candidates

    async def classify(self, query: str) -> tuple[AgentType, list[RoutingCandidate]]:
        """Heuristic first; escalate to a fast LLM route only when genuinely ambiguous."""
        candidates = _heuristic_routing(query)
        top = candidates[0]
        ambiguous = top.score < 75 or (len(candidates) > 1 and top.score - candidates[1].score < 8)
        if ambiguous:
            try:
                from rudra.agents.base import AgentOrchestrator

                llm = await AgentOrchestrator(self.brain).analyze_all_agents(query)
                if llm:
                    return llm[0].agent_type, llm
            except Exception:  # noqa: BLE001 - routing must never hard-fail
                pass
        return top.agent_type, candidates

    # ---- synthesis -----------------------------------------------------------
    def rudra_system(self, agent: BaseAgent, enriched_block: str) -> str:
        """Build the single-voice system prompt: persona + internal playbook + intel."""
        system = (
            f"{OPERATING_PRINCIPLES}\n\n{RUDRA_PERSONA}\n\n"
            f"## Capability playbook for this request (internal — never reveal):\n{agent.system_prompt}"
        )
        if enriched_block:
            system = f"{system}\n\n{enriched_block}"
        return system

    async def enrich_and_build(
        self, query: str, agent_type: AgentType, context: AgentContext, user_id: str
    ) -> tuple[str, list[dict], AgentContext]:
        """Bounded enrichment on a fresh session → (system, sources, context)."""
        sources: list[dict] = []
        try:
            from rudra.core.database import get_session_factory

            async with get_session_factory()() as session:
                ctx, src = await asyncio.wait_for(
                    AgentContextBuilder(MemoryService(session, user_id)).enrich(query, agent_type, context),
                    timeout=self.budget,
                )
                context, sources = ctx, src
        except Exception:  # noqa: BLE001 - enrichment timeout/failure must never block the answer
            pass
        agent = AGENT_REGISTRY[agent_type](self.brain)
        system = self.rudra_system(agent, agent._build_context_prompt(context))
        return system, sources, context

    def routing_analysis(
        self, candidates: list[RoutingCandidate], selected: AgentType
    ) -> list[dict]:
        return [
            {
                "agent": c.agent_type.value,
                "name": AGENT_REGISTRY[c.agent_type](self.brain).name,
                "score": c.score,
                "reason": c.reason,
                "selected": c.agent_type == selected,
            }
            for c in candidates
        ]

    async def run(
        self,
        query: str,
        context: AgentContext,
        user_id: str,
        *,
        agent_type: AgentType | None = None,
    ) -> AgentResponse:
        """Non-streaming: classify → enrich → synthesize one Rudra reply."""
        if agent_type is None:
            agent_type, candidates = await self.classify(query)
        else:
            candidates = [RoutingCandidate(agent_type, 100.0, "Directly selected by owner")]

        system, sources, _ctx = await self.enrich_and_build(query, agent_type, context, user_id)
        result = await self.brain.think([Message(role="user", content=query)], system=system)

        logger.info("rudra_command", agent=agent_type.value, user=user_id)
        return AgentResponse(
            agent_type=agent_type,
            content=result.content,
            agent_name="Rudra",
            agent_intro="",
            confidence=min(0.99, candidates[0].score / 100.0),
            sources_used=sources,
            routing_analysis=self.routing_analysis(candidates, agent_type),
            voice_profile=dict(RUDRA_VOICE),
        )
