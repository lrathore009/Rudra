"""Registry for specialist agent free intelligence sources (agents 2–9)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.core.config import Settings, get_settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.agent_free_sources import (
    concierge,
    librarian,
    luxury,
    operations,
    presentation,
    research,
    travel_agent,
    writing,
)

FetchFn = Callable[[Settings, str], Awaitable[list[IntelItem]]]

AGENT_FETCHERS: dict[AgentType, FetchFn] = {
    AgentType.RESEARCH_ANALYST: research.fetch_research_intel,
    AgentType.CONCIERGE: concierge.fetch_concierge_intel,
    AgentType.LUXURY_ANALYST: luxury.fetch_luxury_intel,
    AgentType.TRAVEL: travel_agent.fetch_travel_intel,
    AgentType.KNOWLEDGE_LIBRARIAN: librarian.fetch_librarian_intel,
    AgentType.WRITING: writing.fetch_writing_intel,
    AgentType.PRESENTATION: presentation.fetch_presentation_intel,
    AgentType.OPERATIONS: operations.fetch_operations_intel,
}

AGENT_SOURCE_CATALOG: dict[AgentType, list[dict[str, str]]] = {
    AgentType.RESEARCH_ANALYST: [
        {"id": "arxiv", "name": "arXiv", "tier": "free", "needs_key": "false"},
        {"id": "sec_edgar", "name": "SEC EDGAR", "tier": "free", "needs_key": "false"},
        {"id": "openalex", "name": "OpenAlex", "tier": "free", "needs_key": "false"},
        {"id": "pubmed", "name": "PubMed", "tier": "free", "needs_key": "false"},
        {"id": "crossref", "name": "Crossref", "tier": "free", "needs_key": "false"},
        {"id": "doaj", "name": "DOAJ", "tier": "free", "needs_key": "false"},
        {"id": "rss", "name": "RSS feeds", "tier": "free", "needs_key": "false"},
    ],
    AgentType.CONCIERGE: [
        {"id": "nominatim", "name": "OpenStreetMap/Nominatim", "tier": "free", "needs_key": "false"},
        {"id": "wikidata", "name": "Wikidata venues", "tier": "free", "needs_key": "false"},
        {"id": "food_rss", "name": "Eater / dining RSS", "tier": "free", "needs_key": "false"},
        {"id": "yelp", "name": "Yelp Fusion", "tier": "optional", "needs_key": "YELP_API_KEY"},
    ],
    AgentType.LUXURY_ANALYST: [
        {"id": "coingecko", "name": "CoinGecko", "tier": "free", "needs_key": "false"},
        {"id": "gdelt", "name": "GDELT luxury signals", "tier": "free", "needs_key": "false"},
        {"id": "wikidata", "name": "Luxury brand entities", "tier": "free", "needs_key": "false"},
        {"id": "luxury_rss", "name": "Robb Report RSS", "tier": "free", "needs_key": "false"},
        {"id": "artsy", "name": "Artsy", "tier": "optional", "needs_key": "ARTSY_API_KEY"},
        {"id": "chrono24", "name": "Chrono24", "tier": "optional", "needs_key": "CHRONO24_API_KEY"},
    ],
    AgentType.TRAVEL: [
        {"id": "restcountries", "name": "RestCountries", "tier": "free", "needs_key": "false"},
        {"id": "nominatim", "name": "Nominatim geocoding", "tier": "free", "needs_key": "false"},
        {"id": "opensky", "name": "OpenSky flights", "tier": "free", "needs_key": "false"},
        {"id": "open_meteo", "name": "Open-Meteo weather", "tier": "free", "needs_key": "false"},
        {"id": "wikipedia", "name": "Visa Wikipedia", "tier": "free", "needs_key": "false"},
        {"id": "amadeus", "name": "Amadeus sandbox", "tier": "optional", "needs_key": "AMADEUS_*"},
    ],
    AgentType.KNOWLEDGE_LIBRARIAN: [
        {"id": "wikidata", "name": "Wikidata", "tier": "free", "needs_key": "false"},
        {"id": "dbpedia", "name": "DBpedia", "tier": "free", "needs_key": "false"},
        {"id": "openalex", "name": "OpenAlex", "tier": "free", "needs_key": "false"},
        {"id": "loc", "name": "Library of Congress", "tier": "free", "needs_key": "false"},
        {"id": "gutenberg", "name": "Project Gutenberg", "tier": "free", "needs_key": "false"},
        {"id": "europeana", "name": "Europeana", "tier": "optional", "needs_key": "EUROPEANA_API_KEY"},
    ],
    AgentType.WRITING: [
        {"id": "datamuse", "name": "Datamuse vocabulary", "tier": "free", "needs_key": "false"},
        {"id": "quotable", "name": "Quotable.io", "tier": "free", "needs_key": "false"},
        {"id": "wikipedia", "name": "Wikipedia references", "tier": "free", "needs_key": "false"},
        {"id": "gdelt", "name": "GDELT context", "tier": "free", "needs_key": "false"},
    ],
    AgentType.PRESENTATION: [
        {"id": "owid", "name": "Our World in Data", "tier": "free", "needs_key": "false"},
        {"id": "worldbank", "name": "World Bank stats", "tier": "free", "needs_key": "false"},
        {"id": "nasa", "name": "NASA APOD", "tier": "free", "needs_key": "NASA_API_KEY (demo ok)"},
        {"id": "openalex", "name": "OpenAlex slide sources", "tier": "free", "needs_key": "false"},
        {"id": "unsplash", "name": "Unsplash visuals", "tier": "optional", "needs_key": "UNSPLASH_ACCESS_KEY"},
    ],
    AgentType.OPERATIONS: [
        {"id": "openfda", "name": "OpenFDA recalls", "tier": "free", "needs_key": "false"},
        {"id": "cdc", "name": "CDC open data", "tier": "free", "needs_key": "false"},
        {"id": "data.gov", "name": "data.gov vendors", "tier": "free", "needs_key": "false"},
        {"id": "open_meteo", "name": "Weather for maintenance", "tier": "free", "needs_key": "false"},
        {"id": "wikidata", "name": "Vendor entities", "tier": "free", "needs_key": "false"},
    ],
}


class AgentFreeSourcesRegistry:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    @property
    def enabled(self) -> bool:
        return self.settings.enable_agent_free_sources

    async def fetch(self, agent_type: AgentType, query: str = "", *, limit: int = 8) -> list[IntelItem]:
        if not self.enabled or agent_type == AgentType.EXECUTIVE_ASSISTANT:
            return []
        fetcher = AGENT_FETCHERS.get(agent_type)
        if not fetcher:
            return []
        try:
            return await fetcher(self.settings, query, limit=limit)
        except Exception:
            return []

    def list_status(self, agent_type: AgentType | None = None) -> list[dict]:
        types = [agent_type] if agent_type else list(AGENT_SOURCE_CATALOG.keys())
        rows: list[dict] = []
        s = self.settings
        key_map = {
            "YELP_API_KEY": bool(getattr(s, "yelp_api_key", None)),
            "ARTSY_API_KEY": bool(s.artsy_api_key),
            "CHRONO24_API_KEY": bool(s.chrono24_api_key),
            "AMADEUS_*": bool(s.amadeus_api_key and s.amadeus_api_secret),
            "EUROPEANA_API_KEY": bool(getattr(s, "europeana_api_key", None)),
            "UNSPLASH_ACCESS_KEY": bool(getattr(s, "unsplash_access_key", None)),
            "NASA_API_KEY (demo ok)": True,
        }
        for at in types:
            catalog = AGENT_SOURCE_CATALOG.get(at, [])
            for src in catalog:
                needs = src.get("needs_key", "false")
                connected = needs == "false" or key_map.get(needs, False)
                rows.append(
                    {
                        "agent": at.value,
                        "source_id": src["id"],
                        "name": src["name"],
                        "tier": src["tier"],
                        "connected": connected and self.enabled,
                    }
                )
        return rows

    async def sync(
        self,
        session: AsyncSession,
        user_id: str,
        agent_type: AgentType,
        query: str = "",
    ) -> dict[str, int]:
        items = await self.fetch(agent_type, query)
        if not items:
            return {"synced": 0}
        data = AgentDataService(session, user_id)
        count = 0
        for item in items[:12]:
            await data.create_artifact(
                agent_type,
                "free_intel",
                item.title[:512],
                item.content[:4000],
                metadata={"provider": item.provider, "category": item.category, "url": item.url},
                status="active",
            )
            count += 1
        return {"synced": count}

    async def sync_all(self, session: AsyncSession, user_id: str) -> dict[str, int]:
        totals: dict[str, int] = {}
        for agent_type in AGENT_FETCHERS:
            result = await self.sync(session, user_id, agent_type)
            totals[agent_type.value] = result.get("synced", 0)
        return totals
