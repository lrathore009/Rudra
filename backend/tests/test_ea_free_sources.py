"""Tests for EA free intelligence sources."""

from __future__ import annotations

import pytest

from rudra.integrations.providers import NewsHeadline, TaskItem
from rudra.jarvis.connectors.free_sources.hub import FreeSourcesHub


@pytest.mark.asyncio
async def test_free_sources_hub_disabled(monkeypatch):
    monkeypatch.setenv("ENABLE_EA_FREE_SOURCES", "false")
    from rudra.core.config import get_settings

    get_settings.cache_clear()
    hub = FreeSourcesHub()
    assert hub.enabled is False
    assert await hub.tasks() == []
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_free_sources_merges_hackernews(monkeypatch):
    monkeypatch.setenv("ENABLE_EA_FREE_SOURCES", "true")
    from rudra.core.config import get_settings

    get_settings.cache_clear()

    async def fake_hn(*, limit: int = 8):
        return [TaskItem("HN story", "open", provider="hackernews", external_id="1")]

    monkeypatch.setattr(
        "rudra.jarvis.connectors.free_sources.calendar_tasks.fetch_hackernews_tasks",
        fake_hn,
    )
    hub = FreeSourcesHub()
    tasks = await hub.tasks(limit=5)
    assert any(t.provider == "hackernews" for t in tasks)
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_free_sources_deduplicates_news(monkeypatch):
    monkeypatch.setenv("ENABLE_EA_FREE_SOURCES", "true")
    from rudra.core.config import get_settings

    get_settings.cache_clear()

    async def fake_gdelt(*, limit: int = 5):
        return [NewsHeadline("Same headline", "GDELT", "https://a.example")]

    async def fake_reddit(settings, *, limit: int = 5):
        return [NewsHeadline("Same headline", "reddit", "https://b.example")]

    async def fake_guardian(*a, **k):
        return []

    async def fake_newsapi(*a, **k):
        return []

    async def fake_mediastack(*a, **k):
        return []

    monkeypatch.setattr("rudra.jarvis.connectors.free_sources.news_apis.fetch_gdelt_headlines", fake_gdelt)
    monkeypatch.setattr("rudra.jarvis.connectors.free_sources.news_apis.fetch_reddit_headlines", fake_reddit)
    monkeypatch.setattr("rudra.jarvis.connectors.free_sources.news_apis.fetch_guardian_headlines", fake_guardian)
    monkeypatch.setattr("rudra.jarvis.connectors.free_sources.news_apis.fetch_newsapi_headlines", fake_newsapi)
    monkeypatch.setattr("rudra.jarvis.connectors.free_sources.news_apis.fetch_mediastack_headlines", fake_mediastack)

    hub = FreeSourcesHub()
    headlines = await hub.news_headlines(limit=5)
    assert len(headlines) == 1
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_free_sources_status_lists_providers(monkeypatch):
    monkeypatch.setenv("ENABLE_EA_FREE_SOURCES", "true")
    monkeypatch.setenv("FRED_API_KEY", "test-key")
    from rudra.core.config import get_settings

    get_settings.cache_clear()
    hub = FreeSourcesHub()
    rows = await hub.list_status()
    providers = {r["provider"] for r in rows}
    assert "free_fred" in providers
    assert "free_hackernews" in providers
    fred = next(r for r in rows if r["provider"] == "free_fred")
    assert fred["connected"] is True
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_executive_stack_includes_knowledge_tier(require_db, monkeypatch):
    monkeypatch.setenv("ENABLE_EA_FREE_SOURCES", "true")
    from rudra.core.config import get_settings
    from rudra.integrations.executive import ExecutiveCommandService
    from rudra.core.database import get_session_factory

    get_settings.cache_clear()

    async def fake_intel():
        return [{"title": "Paper", "content": "Abstract", "provider": "openalex"}]

    monkeypatch.setattr(
        "rudra.jarvis.connectors.registry.ConnectorHub.knowledge_intel",
        lambda self: fake_intel(),
    )

    factory = get_session_factory()
    async with factory() as session:
        svc = ExecutiveCommandService(session, "owner")
        stack = await svc.get_command_stack()
        assert "knowledge" in stack["tier5"]
    get_settings.cache_clear()
