"""Luxury Intelligence Module — continuously growing UHNI knowledge base."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from rudra.brain.orchestrator import Brain, Message
from rudra.core.logging import get_logger
from rudra.research.engine import ResearchEngine, ResearchResult, SourceType

logger = get_logger(__name__)


class LuxuryCategory(str, Enum):
    HOTELS = "luxury_hotels"
    RESORTS = "resorts"
    PRIVATE_ISLANDS = "private_islands"
    YACHTS = "yachts"
    WATCHES = "watches"
    FINE_ART = "fine_art"
    COLLECTIBLES = "collectibles"
    UHNI_TRENDS = "uhni_trends"
    PRIVATE_AVIATION = "private_aviation"
    LIFESTYLE = "wealth_lifestyle"


@dataclass
class LuxuryIntelligence:
    category: LuxuryCategory
    subject: str
    briefing: str
    key_facts: list[str] = field(default_factory=list)
    exclusivity_score: float = 0.5  # 0=accessible, 1=ultra-exclusive
    investment_relevance: float = 0.0
    sources: list[dict[str, str]] = field(default_factory=list)
    related_entities: list[str] = field(default_factory=list)
    last_updated: str | None = None


LUXURY_DOMAIN_PROMPTS = {
    LuxuryCategory.HOTELS: "Focus on: service excellence, exclusivity, recent renovations, signature experiences, UHNI amenities.",
    LuxuryCategory.WATCHES: "Focus on: horological significance, investment trajectory, rarity, auction results, collector sentiment.",
    LuxuryCategory.FINE_ART: "Focus on: provenance, market comparables, artist trajectory, auction history, authentication considerations.",
    LuxuryCategory.PRIVATE_AVIATION: "Focus on: aircraft types, operators, routes, membership models, safety records, cost structures.",
    LuxuryCategory.UHNI_TRENDS: "Focus on: wealth migration patterns, luxury consumption shifts, emerging UHNI destinations, generational preferences.",
}


class LuxuryIntelligenceService:
    """Dedicated luxury research and knowledge accumulation system."""

    def __init__(self, brain: Brain | None = None):
        self.brain = brain or Brain()
        self.research = ResearchEngine(self.brain)

    async def research(
        self,
        subject: str,
        category: LuxuryCategory,
        *,
        depth: str = "standard",
    ) -> LuxuryIntelligence:
        domain_context = LUXURY_DOMAIN_PROMPTS.get(category, "")
        query = f"{category.value.replace('_', ' ')}: {subject}"

        research_result = await self.research.research(
            query,
            sources=[SourceType.WEB, SourceType.NEWS],
            max_sources=15 if depth == "deep" else 8,
        )

        briefing = await self._generate_luxury_briefing(
            subject, category, research_result, domain_context
        )

        intelligence = LuxuryIntelligence(
            category=category,
            subject=subject,
            briefing=briefing["content"],
            key_facts=briefing["key_facts"],
            exclusivity_score=briefing.get("exclusivity_score", 0.5),
            investment_relevance=briefing.get("investment_relevance", 0.0),
            sources=[
                {"title": s.title, "url": s.url}
                for s in research_result.sources
            ],
            related_entities=briefing.get("related_entities", []),
        )

        logger.info(
            "luxury_intelligence_generated",
            category=category.value,
            subject=subject[:60],
        )

        return intelligence

    async def trend_briefing(self, focus_areas: list[LuxuryCategory] | None = None) -> str:
        areas = focus_areas or list(LuxuryCategory)
        areas_str = ", ".join(a.value for a in areas)

        result = await self.brain.think(
            [Message(role="user", content=f"Generate a UHNI luxury trend briefing covering: {areas_str}")],
            system="""You are a luxury intelligence analyst serving ultra-high-net-worth clients.
Provide a concise weekly-style briefing: Top Trends, Notable Openings/Closings, 
Market Movements, Exclusive Opportunities, Watch List. Be specific with names and dates.""",
            model_tier="reasoning",
        )
        return result.content

    async def compare(
        self, subject_a: str, subject_b: str, category: LuxuryCategory
    ) -> str:
        prompt = f"""Compare these two {category.value.replace('_', ' ')} options for a UHNI client:
A: {subject_a}
B: {subject_b}

Provide: Comparison Matrix, Recommendation, Decision Factors, Hidden Considerations."""

        result = await self.brain.think(
            [Message(role="user", content=prompt)],
            system="You are a discreet luxury advisor. Be objective, specific, and actionable.",
        )
        return result.content

    async def _generate_luxury_briefing(
        self,
        subject: str,
        category: LuxuryCategory,
        research: ResearchResult,
        domain_context: str,
    ) -> dict[str, Any]:
        prompt = f"""Generate a luxury intelligence briefing.

Subject: {subject}
Category: {category.value}
Domain Focus: {domain_context}

Research Summary:
{research.summary}

Structure your response as:
## Briefing
(main content)

## Key Facts
- (bullet points)

## Exclusivity Score
(0.0 to 1.0 with brief justification)

## Investment Relevance
(0.0 to 1.0 with brief justification)

## Related Entities
(comma-separated list)"""

        result = await self.brain.think(
            [Message(role="user", content=prompt)],
            system="You are Rudra's Luxury Intelligence Analyst. Institutional-grade, discreet, precise.",
        )

        content = result.content
        key_facts = [
            line.strip("- •")
            for line in content.split("\n")
            if line.strip().startswith(("-", "•"))
        ][:8]

        return {
            "content": content,
            "key_facts": key_facts,
            "exclusivity_score": 0.7,
            "investment_relevance": 0.5,
            "related_entities": [],
        }
