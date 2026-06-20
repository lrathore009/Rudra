"""Build enriched agent context from memories, research, skills, and peer network."""

from __future__ import annotations

from typing import Any

from rudra.agents.base import AgentContext
from rudra.agents.types import AgentType
from rudra.agents.profiles import AGENT_PROFILES
from rudra.core.config import get_settings
from rudra.core.logging import get_logger
from rudra.memory.service import MemoryService
from rudra.research.engine import ResearchEngine, SourceType

logger = get_logger(__name__)


class AgentContextBuilder:
    """Pull domain-relevant data into agent context before execution."""

    def __init__(self, memory_service: MemoryService | None = None):
        self.memory_service = memory_service
        self.research = ResearchEngine()

    async def enrich(
        self,
        query: str,
        agent_type: AgentType,
        context: AgentContext,
    ) -> tuple[AgentContext, list[dict[str, str]]]:
        settings = get_settings()
        heavy = settings.command_enrichment == "full"
        profile = AGENT_PROFILES[agent_type]
        sources_used: list[dict[str, str]] = []
        blocks: list[str] = []

        # Semantic memories — primary personal knowledge source.
        if self.memory_service and "semantic_search" in profile.data_sources:
            try:
                from rudra.brain.embeddings import embed_text

                embedding = await embed_text(query)
                hits = await self.memory_service.search_semantic(
                    embedding, limit=8, min_similarity=0.55
                )
                if hits:
                    blocks.append("## Semantic Memory Matches\n")
                    for mem, score in hits:
                        blocks.append(
                            f"- [{mem.memory_type}] {mem.title} "
                            f"(relevance {score:.2f}): "
                            f"{(mem.summary or mem.content)[:300]}"
                        )
                        sources_used.append(
                            {"type": "memory", "title": mem.title, "id": str(mem.id)}
                        )
            except Exception as e:  # noqa: BLE001
                logger.warning("context_memory_search_failed", error=str(e)[:120])

        # Tag-filtered recent memories for domain focus.
        if context.memories:
            blocks.append("\n## Recent Interaction Context\n")
            for mem in context.memories[:8]:
                blocks.append(
                    f"- [{mem.get('type', 'memory')}] {mem.get('title')}: "
                    f"{mem.get('content', '')[:200]}"
                )

        # Live web + Wikipedia research (full enrichment only — too slow for Vercel proxy).
        if heavy and (profile.use_web_research or profile.use_wikipedia):
            try:
                source_types: list[SourceType] = []
                if profile.use_web_research:
                    source_types.append(SourceType.WEB)
                if profile.use_wikipedia:
                    source_types.append(SourceType.ACADEMIC)
                result = await self.research.research(
                    query,
                    sources=source_types or [SourceType.WEB],
                    max_sources=6,
                    user_memories=context.memories[:5] if context.memories else None,
                )
                if result.sources:
                    blocks.append("\n## Live Intelligence Sources\n")
                    blocks.append(result.summary[:2500])
                    for s in result.sources[:6]:
                        blocks.append(f"- [{s.source_type.value}] {s.title}: {s.snippet[:180]}")
                        sources_used.append(
                            {"type": s.source_type.value, "title": s.title, "url": s.url}
                        )
            except Exception as e:  # noqa: BLE001
                logger.warning("context_research_failed", error=str(e)[:120])

        # Luxury intelligence module (full enrichment only).
        if heavy and profile.use_luxury_intel:
            try:
                from rudra.knowledge.luxury import LuxuryCategory, LuxuryIntelligenceService

                luxury = LuxuryIntelligenceService()
                category = _guess_luxury_category(query)
                intel = await luxury.research(query[:120], category, depth="standard")
                blocks.append("\n## Luxury Intelligence Brief\n")
                blocks.append(intel.briefing[:2000])
                for fact in intel.key_facts[:5]:
                    blocks.append(f"- {fact}")
                sources_used.append(
                    {"type": "luxury_intel", "title": intel.subject, "category": category.value}
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("context_luxury_failed", error=str(e)[:120])

        # Skills loaded for this agent domain.
        if "skills" in profile.data_sources:
            try:
                from rudra.skills.loader import get_skill_registry

                skills = get_skill_registry().list()
                if skills:
                    blocks.append("\n## Available Skills\n")
                    for sk in skills[:4]:
                        blocks.append(f"- {sk['name']}: {sk['description'][:120]}")
                        sources_used.append({"type": "skill", "title": sk["name"]})
            except Exception as e:  # noqa: BLE001
                logger.warning("context_skills_failed", error=str(e)[:120])

        # Single-voice contract: the "peer specialists" network block is intentionally NOT
        # injected into the prompt — it leaked sub-agent framing into Rudra's replies. Cross-
        # domain enrichment still happens silently via the phase-encoded data below.

        # Phase-encoded domain data (preferences, artifacts, reports, graph, etc.).
        if self.memory_service is not None:
            try:
                from rudra.agents.data.enrichment import enrich_agent_phase

                await enrich_agent_phase(
                    query,
                    agent_type,
                    self.memory_service.session,
                    context.user_id,
                    blocks,
                    sources_used,
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("phase_enrichment_failed", agent=agent_type.value, error=str(e)[:120])

        enriched = AgentContext(
            user_id=context.user_id,
            session_id=context.session_id,
            memories=context.memories,
            preferences=context.preferences,
            metadata={
                **context.metadata,
                "enriched_sources": sources_used,
                "enriched_context": "\n".join(blocks),
            },
        )
        return enriched, sources_used


def _guess_luxury_category(query: str) -> Any:
    from rudra.knowledge.luxury import LuxuryCategory

    q = query.lower()
    if any(w in q for w in ("hotel", "resort", "aman", "four seasons")):
        return LuxuryCategory.HOTELS
    if any(w in q for w in ("watch", "patek", "rolex", "horology")):
        return LuxuryCategory.WATCHES
    if any(w in q for w in ("yacht", " charter")):
        return LuxuryCategory.YACHTS
    if any(w in q for w in ("jet", "aviation", "private flight")):
        return LuxuryCategory.PRIVATE_AVIATION
    if any(w in q for w in ("art", "auction", "gallery")):
        return LuxuryCategory.FINE_ART
    return LuxuryCategory.LIFESTYLE
