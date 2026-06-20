"""Tests for specialist agent free intelligence sources (agents 2–9)."""

from __future__ import annotations

import pytest

from rudra.agents.types import AgentType
from rudra.jarvis.connectors.agent_free_sources.registry import AgentFreeSourcesRegistry


@pytest.mark.asyncio
async def test_agent_free_sources_disabled(monkeypatch):
    monkeypatch.setenv("ENABLE_AGENT_FREE_SOURCES", "false")
    from rudra.core.config import get_settings

    get_settings.cache_clear()
    registry = AgentFreeSourcesRegistry()
    assert registry.enabled is False
    assert await registry.fetch(AgentType.RESEARCH_ANALYST, "ai") == []
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_agent_free_sources_catalog():
    registry = AgentFreeSourcesRegistry()
    rows = registry.list_status(AgentType.TRAVEL)
    ids = {r["source_id"] for r in rows}
    assert "restcountries" in ids
    assert "opensky" in ids


@pytest.mark.asyncio
async def test_research_intel_mocked(monkeypatch):
    monkeypatch.setenv("ENABLE_AGENT_FREE_SOURCES", "true")
    from rudra.core.config import get_settings

    get_settings.cache_clear()

    async def fake_fetch(settings, query, *, limit=8):
        from rudra.jarvis.connectors.agent_free_sources._types import IntelItem

        return [IntelItem("Paper", "Abstract", "arxiv", "academic")]

    monkeypatch.setattr(
        "rudra.jarvis.connectors.agent_free_sources.registry.AGENT_FETCHERS",
        {AgentType.RESEARCH_ANALYST: fake_fetch},
    )
    registry = AgentFreeSourcesRegistry()
    items = await registry.fetch(AgentType.RESEARCH_ANALYST, "ai")
    assert len(items) == 1
    assert items[0].provider == "arxiv"
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_sync_free_sources_tool(require_db, monkeypatch):
    monkeypatch.setenv("ENABLE_AGENT_FREE_SOURCES", "true")
    from rudra.core.config import get_settings
    from rudra.agents.phase_tools import sync_free_sources
    from rudra.agents.tools import ToolContext

    get_settings.cache_clear()

    async def fake_fetch(settings, query, *, limit=8):
        from rudra.jarvis.connectors.agent_free_sources._types import IntelItem

        return [IntelItem("Signal", "Content", "gdelt", "news")]

    monkeypatch.setattr(
        "rudra.jarvis.connectors.agent_free_sources.research.fetch_research_intel",
        fake_fetch,
    )

    factory = __import__("rudra.core.database", fromlist=["get_session_factory"]).get_session_factory()
    async with factory() as session:
        ctx = ToolContext(db=session, user_id="owner")
        msg = await sync_free_sources({"agent": "research_analyst", "query": "ai"}, ctx)
        await session.commit()
        assert "Synced" in msg
    get_settings.cache_clear()


def test_all_specialists_have_free_source_tools(client, require_db):
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    for slug in (
        "research_analyst",
        "concierge",
        "luxury_analyst",
        "travel",
        "knowledge_librarian",
        "writing",
        "presentation",
        "operations",
    ):
        agent = next(a for a in res.json() if a["type"] == slug)
        tools = agent["phase"]["tools"]
        assert "sync_free_sources" in tools
        assert "list_free_source_status" in tools
