"""Agent encoded data seed and enrichment tests."""

import pytest

from rudra.agents.data.seed import seed_agent_phase_data
from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.core.database import get_session_factory
from rudra.research.reports import ResearchReportService


@pytest.mark.asyncio
async def test_seed_agent_phase_data(require_db):
    factory = get_session_factory()
    async with factory() as session:
        counts = await seed_agent_phase_data(session, "owner")
        await session.commit()
        assert counts["preferences"] >= 10

        data = AgentDataService(session, "owner")
        watchlist = await data.list_artifacts(AgentType.LUXURY_ANALYST, artifact_type="watchlist")
        assert len(watchlist) >= 1

        reports = ResearchReportService(session, "owner")
        library = await reports.list_recent(limit=5)
        assert len(library) >= 1


@pytest.mark.asyncio
async def test_seed_is_idempotent(require_db):
    factory = get_session_factory()
    async with factory() as session:
        first = await seed_agent_phase_data(session, "owner")
        await session.commit()
        second = await seed_agent_phase_data(session, "owner")
        await session.commit()
        assert second["watchlist"] == 0
        assert second["research_reports"] == 0
        assert first["preferences"] > 0
