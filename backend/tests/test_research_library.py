"""Phase 2 research library tests."""

import pytest

from rudra.agents.data.seed import seed_agent_phase_data
from rudra.core.database import get_session_factory
from rudra.jarvis.federation import export_memories, register_device
from rudra.research.hybrid import hybrid_search_reports
from rudra.research.reports import ResearchReportService


@pytest.mark.asyncio
async def test_research_watchlist_seed(require_db):
    factory = get_session_factory()
    async with factory() as session:
        counts = await seed_agent_phase_data(session, "owner")
        await session.commit()
        svc = ResearchReportService(session, "owner")
        watchlist = await svc.list_watchlist()
        assert counts["research_watchlist"] >= 3 or len(watchlist) >= 3


@pytest.mark.asyncio
async def test_add_watchlist_and_trends(require_db):
    factory = get_session_factory()
    async with factory() as session:
        svc = ResearchReportService(session, "owner")
        await svc.save(
            title="Test report",
            query="agent orchestration patterns",
            content="Executive summary with agent orchestration and ReAct routing.",
            confidence_score=0.9,
        )
        await svc.add_watchlist("Test topic", "agent orchestration ReAct")
        await session.commit()

        trends = await svc.trends()
        assert trends["count"] >= 1
        assert trends["avg_confidence"] > 0

        watchlist = await svc.list_watchlist()
        assert any(w.topic == "Test topic" for w in watchlist)


@pytest.mark.asyncio
async def test_hybrid_search_reports(require_db):
    factory = get_session_factory()
    async with factory() as session:
        svc = ResearchReportService(session, "owner")
        await svc.save(
            title="Local-first AI scan",
            query="local-first personal AI",
            content="Privacy-first local AI with Ollama and pgvector embeddings.",
            confidence_score=0.85,
        )
        await session.commit()

        hits = await hybrid_search_reports(svc, "local-first AI", limit=5)
        assert hits
        assert any("local" in r.title.lower() or "local" in r.content.lower() for r, _ in hits)


@pytest.mark.asyncio
async def test_federation_export_includes_research(require_db):
    factory = get_session_factory()
    async with factory() as session:
        svc = ResearchReportService(session, "owner")
        await svc.save(
            title="Federation research",
            query="federation sync test",
            content="Report body for federation export.",
            confidence_score=0.8,
        )
        creds = await register_device(session, "owner", "test-device")
        await session.commit()

        payload = await export_memories(session, "owner", creds["sync_token"])
        await session.commit()
        assert any(item.get("type") == "research_report" for item in payload)


@pytest.mark.asyncio
async def test_research_phase_tools_registered(client, require_db):
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    agents = res.json()
    research = next(a for a in agents if a["type"] == "research_analyst")
    tools = set(research.get("phase", {}).get("tools", []))
    assert "hybrid_search_library" in tools
    assert "add_research_watchlist" in tools
    assert "research_library_trends" in tools
