"""Phase 1 executive command stack tests."""

import pytest

from rudra.integrations.executive import ExecutiveCommandService
from rudra.core.database import get_session_factory


@pytest.mark.asyncio
async def test_executive_command_stack(require_db):
    factory = get_session_factory()
    async with factory() as session:
        svc = ExecutiveCommandService(session, "owner")
        await svc.connect_mock_stack()
        await session.commit()
        stack = await svc.get_command_stack()
        assert stack["tier1"]["calendar"]
        assert stack["tier1"]["tasks"]
        assert stack["tier2"]["weather"]
        assert "projects" in stack


@pytest.mark.asyncio
async def test_executive_sync_and_commitments(require_db):
    factory = get_session_factory()
    async with factory() as session:
        svc = ExecutiveCommandService(session, "owner")
        counts = await svc.sync_all()
        await session.commit()
        assert counts["calendar"] >= 1
        commitments = await svc.list_commitments()
        assert isinstance(commitments, list)


def test_ea_phase_tools_registered(client, require_db):
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    ea = next(a for a in res.json() if a["type"] == "executive_assistant")
    tools = ea["phase"]["tools"]
    assert "get_command_stack" in tools
    assert "sync_executive_sources" in tools
    assert "list_commitments" in tools
