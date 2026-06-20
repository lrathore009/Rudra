"""Orchestrates all free EA intelligence sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings, get_settings
from rudra.integrations.providers import (
    CalendarEvent,
    CommandFeedItem,
    ContactRecord,
    DocumentRef,
    EmailMessage,
    FinanceLine,
    HealthReading,
    NewsHeadline,
    TaskItem,
    TravelConfirmation,
)
from rudra.jarvis.connectors.free_sources import calendar_tasks, contacts_knowledge, email_docs
from rudra.jarvis.connectors.free_sources import finance_apis, health_apis, news_apis, travel_apis


class FreeSourcesHub:
    """Aggregates configured free-tier sources for the EA command stack."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    @property
    def enabled(self) -> bool:
        return self.settings.enable_ea_free_sources

    async def calendar_events(self) -> list[CalendarEvent]:
        if not self.enabled:
            return []
        results = await asyncio.gather(
            calendar_tasks.fetch_ical_events(self.settings),
            return_exceptions=True,
        )
        out: list[CalendarEvent] = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out

    async def tasks(self, *, limit: int = 10) -> list[TaskItem]:
        if not self.enabled:
            return []
        results = await asyncio.gather(
            calendar_tasks.fetch_todoist_tasks(self.settings, limit=limit),
            calendar_tasks.fetch_github_tasks(self.settings, limit=limit),
            calendar_tasks.fetch_trello_tasks(self.settings, limit=limit),
            calendar_tasks.fetch_hackernews_tasks(limit=8),
            return_exceptions=True,
        )
        out: list[TaskItem] = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out[:limit]

    async def recent_emails(self, *, limit: int = 8) -> list[EmailMessage]:
        if not self.enabled:
            return []
        return await email_docs.fetch_imap_emails(self.settings, limit=limit)

    async def documents(self, *, limit: int = 10) -> list[DocumentRef]:
        if not self.enabled:
            return []
        obsidian, archive = await asyncio.gather(
            email_docs.fetch_obsidian_documents(self.settings, limit=limit),
            email_docs.fetch_archive_context(self.settings, limit=3),
            return_exceptions=True,
        )
        out: list[DocumentRef] = []
        if isinstance(obsidian, list):
            out.extend(obsidian)
        if isinstance(archive, list):
            out.extend(archive)
        return out[:limit]

    async def news_headlines(self, *, limit: int = 10) -> list[NewsHeadline]:
        if not self.enabled:
            return []
        results = await asyncio.gather(
            news_apis.fetch_gdelt_headlines(limit=5),
            news_apis.fetch_guardian_headlines(self.settings, limit=5),
            news_apis.fetch_newsapi_headlines(self.settings, limit=5),
            news_apis.fetch_mediastack_headlines(self.settings, limit=5),
            news_apis.fetch_reddit_headlines(self.settings, limit=5),
            return_exceptions=True,
        )
        out: list[NewsHeadline] = []
        seen: set[str] = set()
        for r in results:
            if not isinstance(r, list):
                continue
            for h in r:
                key = h.title[:80]
                if key in seen:
                    continue
                seen.add(key)
                out.append(h)
                if len(out) >= limit:
                    return out
        return out

    async def finance_lines(self) -> list[FinanceLine]:
        if not self.enabled:
            return []
        results = await asyncio.gather(
            finance_apis.fetch_fred_lines(self.settings),
            finance_apis.fetch_alpha_vantage_lines(self.settings),
            finance_apis.fetch_coingecko_lines(),
            finance_apis.fetch_edgar_finance_lines(self.settings),
            finance_apis.fetch_companies_house_lines(self.settings),
            finance_apis.fetch_worldbank_lines(),
            finance_apis.fetch_imf_lines(),
            return_exceptions=True,
        )
        out: list[FinanceLine] = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out

    async def travel_confirmations(self) -> list[TravelConfirmation]:
        if not self.enabled:
            return []
        results = await asyncio.gather(
            travel_apis.fetch_amadeus_travel(self.settings),
            travel_apis.fetch_opensky_travel(),
            travel_apis.fetch_restcountries_travel(self.settings),
            travel_apis.fetch_nominatim_travel(self.settings),
            return_exceptions=True,
        )
        out: list[TravelConfirmation] = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out

    async def health_readings(self) -> list[HealthReading]:
        if not self.enabled:
            return []
        results = await asyncio.gather(
            health_apis.fetch_openfda_readings(),
            health_apis.fetch_pubmed_readings(),
            health_apis.fetch_cdc_readings(),
            health_apis.fetch_health_export_readings(self.settings),
            return_exceptions=True,
        )
        out: list[HealthReading] = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out

    async def contacts(self, *, limit: int = 10) -> list[ContactRecord]:
        if not self.enabled:
            return []
        results = await asyncio.gather(
            contacts_knowledge.fetch_wikidata_contacts(self.settings),
            contacts_knowledge.fetch_dbpedia_contacts(self.settings),
            contacts_knowledge.fetch_gravatar_contacts(self.settings),
            return_exceptions=True,
        )
        out: list[ContactRecord] = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out[:limit]

    async def knowledge_intel(self) -> list[CommandFeedItem]:
        if not self.enabled:
            return []
        results = await asyncio.gather(
            contacts_knowledge.fetch_openalex_intel(self.settings),
            contacts_knowledge.fetch_semantic_scholar_intel(self.settings),
            contacts_knowledge.fetch_nasa_intel(self.settings),
            contacts_knowledge.fetch_eurostat_intel(),
            contacts_knowledge.fetch_datagov_intel(),
            return_exceptions=True,
        )
        out: list[CommandFeedItem] = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out

    async def list_status(self) -> list[dict]:
        s = self.settings
        return [
            {"provider": "free_caldav", "connected": bool(s.ea_caldav_urls), "tier": 1},
            {"provider": "free_todoist", "connected": bool(s.ea_todoist_token), "tier": 1},
            {"provider": "free_github", "connected": bool(s.ea_github_repos), "tier": 1},
            {"provider": "free_trello", "connected": bool(s.ea_trello_board_id), "tier": 1},
            {"provider": "free_hackernews", "connected": s.enable_ea_free_sources, "tier": 1},
            {"provider": "free_imap", "connected": bool(s.ea_imap_host and s.ea_imap_user), "tier": 1},
            {"provider": "free_obsidian", "connected": bool(s.ea_obsidian_vault_path), "tier": 2},
            {"provider": "free_internet_archive", "connected": s.enable_ea_free_sources, "tier": 2},
            {"provider": "free_gdelt", "connected": s.enable_ea_free_sources, "tier": 2},
            {"provider": "free_guardian", "connected": bool(s.guardian_api_key), "tier": 2},
            {"provider": "free_newsapi", "connected": bool(s.newsapi_key), "tier": 2},
            {"provider": "free_mediastack", "connected": bool(s.mediastack_api_key), "tier": 2},
            {"provider": "free_reddit", "connected": s.enable_ea_free_sources, "tier": 2},
            {"provider": "free_fred", "connected": bool(s.fred_api_key), "tier": 2},
            {"provider": "free_alpha_vantage", "connected": bool(s.alpha_vantage_api_key), "tier": 2},
            {"provider": "free_coingecko", "connected": s.enable_ea_free_sources, "tier": 2},
            {"provider": "free_edgar", "connected": s.enable_ea_free_sources, "tier": 2},
            {"provider": "free_companies_house", "connected": bool(s.companies_house_api_key), "tier": 2},
            {"provider": "free_worldbank", "connected": s.enable_ea_free_sources, "tier": 2},
            {"provider": "free_imf", "connected": s.enable_ea_free_sources, "tier": 2},
            {"provider": "free_amadeus", "connected": bool(s.amadeus_api_key and s.amadeus_api_secret), "tier": 3},
            {"provider": "free_opensky", "connected": s.enable_ea_free_sources, "tier": 3},
            {"provider": "free_nominatim", "connected": s.enable_ea_free_sources, "tier": 3},
            {"provider": "free_restcountries", "connected": s.enable_ea_free_sources, "tier": 3},
            {"provider": "free_openfda", "connected": s.enable_ea_free_sources, "tier": 4},
            {"provider": "free_pubmed", "connected": s.enable_ea_free_sources, "tier": 4},
            {"provider": "free_cdc", "connected": s.enable_ea_free_sources, "tier": 4},
            {"provider": "free_health_export", "connected": bool(s.ea_health_export_path), "tier": 4},
            {"provider": "free_wikidata", "connected": s.enable_ea_free_sources, "tier": 1},
            {"provider": "free_openalex", "connected": s.enable_ea_free_sources, "tier": 5},
            {"provider": "free_semantic_scholar", "connected": s.enable_ea_free_sources, "tier": 5},
            {"provider": "free_nasa", "connected": s.enable_ea_free_sources, "tier": 5},
            {"provider": "free_eurostat", "connected": s.enable_ea_free_sources, "tier": 5},
            {"provider": "free_datagov", "connected": s.enable_ea_free_sources, "tier": 5},
        ]
