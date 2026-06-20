"""Agent layer — specialized intelligence modules."""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from rudra.agents.phases import phase_to_dict
from rudra.agents.profiles import AGENT_PROFILES
from rudra.agents.types import AgentType
from rudra.brain.orchestrator import Brain, Message
from rudra.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgentContext:
    user_id: str
    session_id: str
    memories: list[dict[str, Any]] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingCandidate:
    agent_type: AgentType
    score: float
    reason: str


@dataclass
class AgentResponse:
    agent_type: AgentType
    content: str
    agent_name: str = ""
    agent_intro: str = ""
    actions: list[dict[str, Any]] = field(default_factory=list)
    memories_to_store: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    citations: list[dict[str, str]] = field(default_factory=list)
    routing_analysis: list[dict[str, Any]] = field(default_factory=list)
    sources_used: list[dict[str, str]] = field(default_factory=list)
    voice_profile: dict[str, Any] = field(default_factory=dict)


OPERATING_PRINCIPLES = """You are part of Rudra, a private personal intelligence system serving one trusted owner.

Operating principles:
- Fulfill all lawful, legitimate requests directly, thoroughly, and proactively.
- Recreational, travel, and luxury activities — surfing, scuba diving, sightseeing,
  yachting, fine dining, leisure planning — are completely normal and safe. NEVER
  refuse, warn, or moralize about them, and never invent legal or safety restrictions.
- If you lack real-time data, make reasonable, clearly-labeled assumptions and still
  produce a concrete, specific, actionable result. Do not stall.
- Be detailed and high-quality. Prefer structured output (headings, bullets, steps).
- Ground answers in the Intelligence Sources provided below when present — cite them.
- Speak in ONE voice: Rudra. Never introduce yourself, never name or reference a sub-agent,
  "specialist", department, or routing decision. Answer the owner directly, as Rudra.
- Only decline if a request is genuinely illegal or seriously harmful — which ordinary
  travel and leisure never are.
"""


class BaseAgent(ABC):
    agent_type: AgentType
    name: str
    description: str

    def __init__(self, brain: Brain):
        self.brain = brain

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        ...

    def _build_context_prompt(self, context: AgentContext) -> str:
        parts = []
        enriched = context.metadata.get("enriched_context")
        if enriched:
            parts.append(enriched)
        elif context.memories:
            parts.append("## Relevant Memories\n")
            for mem in context.memories[:10]:
                parts.append(
                    f"- [{mem.get('type', 'memory')}] {mem.get('title')}: "
                    f"{mem.get('summary', mem.get('content', ''))[:200]}"
                )
        if context.preferences:
            parts.append("\n## User Preferences\n")
            for k, v in context.preferences.items():
                parts.append(f"- {k}: {v}")
        return "\n".join(parts)

    def build_intro(self) -> str:
        """Deprecated — sub-agent self-introductions are never shown to the owner."""
        return f"I am Rudra's {self.name} — {self.description}."

    def format_response(self, answer: str) -> tuple[str, str]:
        # Single-voice contract: the owner sees Rudra's answer only — no sub-agent intro.
        return "", answer

    async def execute(self, query: str, context: AgentContext) -> AgentResponse:
        context_block = self._build_context_prompt(context)
        system = f"{OPERATING_PRINCIPLES}\n\n{self.system_prompt}"
        if context_block:
            system = f"{system}\n\n{context_block}"

        result = await self.brain.think(
            [Message(role="user", content=query)],
            system=system,
        )

        intro, full = self.format_response(result.content)
        profile = AGENT_PROFILES[self.agent_type]
        sources = context.metadata.get("enriched_sources", [])

        logger.info("agent_executed", agent=self.agent_type.value, user=context.user_id)

        return AgentResponse(
            agent_type=self.agent_type,
            content=full,
            agent_name=self.name,
            agent_intro=intro,
            confidence=0.9,
            sources_used=sources,
            voice_profile={
                "pitch": profile.voice.pitch,
                "rate": profile.voice.rate,
                "voice_hints": list(profile.voice.voice_hints),
            },
        )


class ExecutiveAssistantAgent(BaseAgent):
    agent_type = AgentType.EXECUTIVE_ASSISTANT
    name = "Executive Assistant"
    description = "your chief of staff for priorities, calendar, tasks, and daily briefings"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Executive Assistant — a discreet, highly capable chief of staff.
Your role: prioritize tasks, manage time, prepare briefings, track commitments, and anticipate needs.
Style: concise, proactive, executive-grade. Never verbose. Always actionable.
Format responses with clear sections: Priority Actions, Schedule Notes, Follow-ups."""

    async def execute(self, query: str, context: AgentContext) -> AgentResponse:
        from rudra.core.config import get_settings

        if get_settings().enable_minions_routing:
            from rudra.jarvis.minions import minions_think
            from rudra.jarvis.persona import jarvis_system_prompt

            context_block = self._build_context_prompt(context)
            system = (
                f"{OPERATING_PRINCIPLES}\n\n{self.system_prompt}\n\n"
                f"{jarvis_system_prompt(mode='command')}"
            )
            content, tier = await minions_think(
                self.brain,
                query,
                context=context_block,
                system=system,
            )
            intro, full = self.format_response(content)
            profile = AGENT_PROFILES[self.agent_type]
            sources = list(context.metadata.get("enriched_sources", []))
            sources.append({"type": "minions", "title": f"routing:{tier}"})
            return AgentResponse(
                agent_type=self.agent_type,
                content=full,
                agent_name=self.name,
                agent_intro=intro,
                sources_used=sources,
                voice_profile={
                    "pitch": profile.voice.pitch,
                    "rate": profile.voice.rate,
                    "voice_hints": list(profile.voice.voice_hints),
                },
            )
        return await super().execute(query, context)


class ResearchAnalystAgent(BaseAgent):
    agent_type = AgentType.RESEARCH_ANALYST
    name = "Research Analyst"
    description = "your institutional-grade analyst for deep research with citations and confidence scoring"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Research Analyst — institutional-grade intelligence gathering.
Your role: synthesize information, evaluate source credibility, assign confidence scores, cite sources.
Always structure: Executive Summary, Key Findings, Analysis, Confidence Assessment, Sources.
Mark uncertain claims explicitly. Distinguish fact from inference."""

    async def execute(self, query: str, context: AgentContext) -> AgentResponse:
        from rudra.core.config import get_settings

        if get_settings().enable_minions_routing:
            from rudra.jarvis.minions import minions_think
            from rudra.jarvis.persona import jarvis_system_prompt

            context_block = self._build_context_prompt(context)
            system = (
                f"{OPERATING_PRINCIPLES}\n\n{self.system_prompt}\n\n"
                f"{jarvis_system_prompt(mode='research')}"
            )
            content, tier = await minions_think(
                self.brain,
                query,
                context=context_block,
                system=system,
            )
            intro, full = self.format_response(content)
            profile = AGENT_PROFILES[self.agent_type]
            sources = list(context.metadata.get("enriched_sources", []))
            sources.append({"type": "minions", "title": f"routing:{tier}"})
            return AgentResponse(
                agent_type=self.agent_type,
                content=full,
                agent_name=self.name,
                agent_intro=intro,
                sources_used=sources,
                voice_profile={
                    "pitch": profile.voice.pitch,
                    "rate": profile.voice.rate,
                    "voice_hints": list(profile.voice.voice_hints),
                },
            )
        return await super().execute(query, context)


class ConciergeAgent(BaseAgent):
    agent_type = AgentType.CONCIERGE
    name = "Concierge Specialist"
    description = "your world-class luxury lifestyle and premium service coordinator"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Concierge — a world-class luxury lifestyle specialist.
Your role: curate exceptional experiences, secure reservations, coordinate premium services.
Style: refined, knowledgeable, anticipatory. Know UHNI preferences and discretion standards.
Present options ranked by fit, never overwhelm with choices."""


class LuxuryAnalystAgent(BaseAgent):
    agent_type = AgentType.LUXURY_ANALYST
    name = "Luxury Intelligence Analyst"
    description = "your expert in ultra-high-net-worth lifestyle and luxury market intelligence"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Luxury Intelligence Analyst — expert in ultra-high-net-worth lifestyle.
Domains: luxury hotels, resorts, private islands, yachts, watches, fine art, collectibles,
private aviation, wealth trends, exclusive experiences.
Provide intelligence briefings with market context, exclusivity assessment, and investment perspective.
Maintain awareness of seasonal openings, auction results, and UHNI trend shifts."""


class TravelSpecialistAgent(BaseAgent):
    agent_type = AgentType.TRAVEL
    name = "Travel Specialist"
    description = "your master planner for complex, luxury travel and seamless itineraries"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Travel Specialist — master of complex, luxury travel planning.
Your role: design seamless multi-destination itineraries, handle logistics, anticipate disruptions.
Consider: private aviation connections, visa requirements, seasonal factors, health protocols.
Present itineraries with day-by-day structure, backup options, and contingency plans."""


class KnowledgeLibrarianAgent(BaseAgent):
    agent_type = AgentType.KNOWLEDGE_LIBRARIAN
    name = "Knowledge Librarian"
    description = "your curator of personal knowledge, memories, and connected insights"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Knowledge Librarian — curator of the user's personal knowledge universe.
Your role: organize, retrieve, connect, and synthesize stored knowledge.
When answering, reference specific memories and documents. Suggest knowledge connections.
Help the user build a richer, more interconnected personal knowledge graph over time."""


class WritingAssistantAgent(BaseAgent):
    agent_type = AgentType.WRITING
    name = "Writing Assistant"
    description = "your expert in professional and personal communication across every format"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Writing Assistant — master of professional and personal communication.
Adapt tone to context: board memos, personal letters, speeches, emails, reports.
Match the user's voice when preferences are known. Prioritize clarity, precision, and impact."""


class PresentationBuilderAgent(BaseAgent):
    agent_type = AgentType.PRESENTATION
    name = "Presentation Builder"
    description = "your creator of executive-grade presentations and briefing documents"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Presentation Builder — creator of executive-grade presentations.
Structure content for impact: clear narrative arc, data-driven insights, actionable conclusions.
Output slide outlines with speaker notes, key visuals suggestions, and audience-specific framing."""


class OperationsManagerAgent(BaseAgent):
    agent_type = AgentType.OPERATIONS
    name = "Personal Operations Manager"
    description = "your orchestrator of household logistics, vendors, and recurring operations"

    @property
    def system_prompt(self) -> str:
        return """You are Rudra's Personal Operations Manager — orchestrator of life's logistics.
Your role: coordinate vendors, track household operations, manage recurring tasks, optimize systems.
Be systematic, detail-oriented, and proactive about maintenance schedules and operational efficiency."""


AGENT_REGISTRY: dict[AgentType, type[BaseAgent]] = {
    AgentType.EXECUTIVE_ASSISTANT: ExecutiveAssistantAgent,
    AgentType.RESEARCH_ANALYST: ResearchAnalystAgent,
    AgentType.CONCIERGE: ConciergeAgent,
    AgentType.LUXURY_ANALYST: LuxuryAnalystAgent,
    AgentType.TRAVEL: TravelSpecialistAgent,
    AgentType.KNOWLEDGE_LIBRARIAN: KnowledgeLibrarianAgent,
    AgentType.WRITING: WritingAssistantAgent,
    AgentType.PRESENTATION: PresentationBuilderAgent,
    AgentType.OPERATIONS: OperationsManagerAgent,
}


class AgentOrchestrator:
    """Routes requests across all nine interconnected agents."""

    def __init__(self, brain: Brain | None = None):
        self.brain = brain or Brain()
        self._agents: dict[AgentType, BaseAgent] = {}

    def get_agent(self, agent_type: AgentType) -> BaseAgent:
        if agent_type not in self._agents:
            cls = AGENT_REGISTRY[agent_type]
            self._agents[agent_type] = cls(self.brain)
        return self._agents[agent_type]

    def list_agents(self) -> list[dict[str, Any]]:
        items = []
        for t, cls in AGENT_REGISTRY.items():
            agent = cls(self.brain)
            profile = AGENT_PROFILES[t]
            items.append(
                {
                    "type": t.value,
                    "name": agent.name,
                    "description": agent.description,
                    "data_sources": list(profile.data_sources),
                    "voice_profile": {
                        "pitch": profile.voice.pitch,
                        "rate": profile.voice.rate,
                        "voice_hints": list(profile.voice.voice_hints),
                    },
                    "phase": phase_to_dict(t),
                }
            )
        return items

    async def analyze_all_agents(self, query: str) -> list[RoutingCandidate]:
        """Score all nine agents and return ranked candidates."""
        catalog = "\n".join(
            f"- {t.value}: {cls(self.brain).name} — {cls(self.brain).description}"
            for t, cls in AGENT_REGISTRY.items()
        )
        routing_prompt = f"""Analyze this user request against ALL nine Rudra agents.
For EACH agent, assign a fit score from 0 to 100 and a one-line reason.
Then identify the single best agent to respond.

Agents:
{catalog}

Request: {query}

Reply with ONLY valid JSON (no markdown):
{{"selected":"agent_type_id","candidates":[{{"agent":"agent_type_id","score":85,"reason":"..."}}, ...all nine...]}}"""

        result = await self.brain.think(
            [Message(role="user", content=routing_prompt)],
            model_tier="fast",
        )
        parsed = self._parse_routing_json(result.content, query)
        return parsed

    @staticmethod
    def _parse_routing_json(raw: str, query: str) -> list[RoutingCandidate]:
        text = raw.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                candidates: list[RoutingCandidate] = []
                for item in data.get("candidates", []):
                    try:
                        agent_type = AgentType(item["agent"])
                        candidates.append(
                            RoutingCandidate(
                                agent_type=agent_type,
                                score=float(item.get("score", 0)),
                                reason=str(item.get("reason", ""))[:200],
                            )
                        )
                    except (ValueError, KeyError):
                        continue
                if candidates:
                    return sorted(candidates, key=lambda c: c.score, reverse=True)
                selected_raw = data.get("selected")
                if selected_raw:
                    return [
                        RoutingCandidate(
                            agent_type=AgentType(selected_raw),
                            score=100.0,
                            reason="Primary match",
                        )
                    ]
            except (json.JSONDecodeError, ValueError):
                pass
        # Heuristic fallback when the model returns unstructured text.
        return _heuristic_routing(query)

    async def route(
        self,
        query: str,
        context: AgentContext,
        *,
        memory_service=None,
    ) -> AgentResponse:
        """Analyze all agents, enrich context, execute the best match with self-introduction."""
        candidates = await self.analyze_all_agents(query)
        best = candidates[0]
        agent = self.get_agent(best.agent_type)

        if memory_service is not None:
            from rudra.agents.context_builder import AgentContextBuilder

            context, sources = await AgentContextBuilder(memory_service).enrich(
                query, best.agent_type, context
            )
        else:
            sources = []

        response = await agent.execute(query, context)
        response.routing_analysis = [
            {
                "agent": c.agent_type.value,
                "name": self.get_agent(c.agent_type).name,
                "score": c.score,
                "reason": c.reason,
                "selected": c.agent_type == best.agent_type,
            }
            for c in candidates
        ]
        if sources and not response.sources_used:
            response.sources_used = sources
        response.confidence = min(0.99, best.score / 100.0)
        return response

    @staticmethod
    def _parse_agent_type(raw: str) -> AgentType:
        text = raw.strip().lower()
        try:
            return AgentType(text)
        except ValueError:
            pass
        for t in sorted(AgentType, key=lambda x: len(x.value), reverse=True):
            if t.value in text:
                return t
        return AgentType.EXECUTIVE_ASSISTANT

    async def invoke(
        self,
        agent_type: AgentType,
        query: str,
        context: AgentContext,
        *,
        memory_service=None,
    ) -> AgentResponse:
        if memory_service is not None:
            from rudra.agents.context_builder import AgentContextBuilder

            context, sources = await AgentContextBuilder(memory_service).enrich(
                query, agent_type, context
            )
        else:
            sources = []

        agent = self.get_agent(agent_type)
        response = await agent.execute(query, context)
        if sources and not response.sources_used:
            response.sources_used = sources
        response.routing_analysis = [
            {
                "agent": agent_type.value,
                "name": agent.name,
                "score": 100.0,
                "reason": "Directly selected by user",
                "selected": True,
            }
        ]
        return response


def _heuristic_routing(query: str) -> list[RoutingCandidate]:
    """Keyword-based fallback scoring for all nine agents."""
    q = query.lower()
    rules: list[tuple[AgentType, tuple[str, ...], float]] = [
        (AgentType.RESEARCH_ANALYST, ("research", "analyze", "study", "report", "cite"), 90),
        (AgentType.TRAVEL, ("travel", "trip", "itinerary", "flight", "hotel", "visa", "eiffel", "lanka", "visit"), 92),
        (AgentType.LUXURY_ANALYST, ("luxury", "uhni", "watch", "yacht", "auction", "collectible"), 88),
        (AgentType.CONCIERGE, ("concierge", "reservation", "restaurant", "experience", "dining"), 86),
        (AgentType.KNOWLEDGE_LIBRARIAN, ("remember", "memory", "knowledge", "recall", "library"), 84),
        (AgentType.WRITING, ("write", "email", "letter", "draft", "compose"), 87),
        (AgentType.PRESENTATION, ("presentation", "slide", "deck", "pitch"), 89),
        (AgentType.OPERATIONS, ("vendor", "household", "maintenance", "operations", "logistics"), 83),
        (AgentType.EXECUTIVE_ASSISTANT, ("briefing", "priority", "calendar", "schedule", "day"), 85),
    ]
    scores: dict[AgentType, RoutingCandidate] = {}
    for agent_type, keywords, base in rules:
        hits = sum(1 for kw in keywords if kw in q)
        score = base + hits * 3 if hits else 20.0
        scores[agent_type] = RoutingCandidate(
            agent_type=agent_type,
            score=min(98.0, score),
            reason=f"Keyword match ({hits} signals)" if hits else "General capability",
        )
    if not any(c.score > 50 for c in scores.values()):
        scores[AgentType.EXECUTIVE_ASSISTANT] = RoutingCandidate(
            agent_type=AgentType.EXECUTIVE_ASSISTANT,
            score=75.0,
            reason="Default executive routing",
        )
    return sorted(scores.values(), key=lambda c: c.score, reverse=True)
