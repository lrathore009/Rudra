"""Tests for agent phases 3–9 domain services."""

import pytest

from rudra.agents.data.seed import seed_agent_phase_data
from rudra.core.database import get_session_factory
from rudra.domains.concierge import ExperienceService
from rudra.domains.librarian import LibrarianRetrievalService
from rudra.domains.operations import OpsRunbookService
from rudra.domains.presentation import DeckService
from rudra.domains.travel import TripService
from rudra.domains.writing import DraftService


@pytest.mark.asyncio
async def test_librarian_unified_search(require_db):
    factory = get_session_factory()
    async with factory() as session:
        svc = LibrarianRetrievalService(session, "owner")
        result = await svc.answer("Rudra personal intelligence")
        await session.commit()
        assert result["trace_id"]
        assert "sources" in result


@pytest.mark.asyncio
async def test_concierge_request_pipeline(require_db):
    factory = get_session_factory()
    async with factory() as session:
        svc = ExperienceService(session, "owner")
        row = await svc.log_request("Test dinner", "4 guests omakase")
        await session.commit()
        open_rows = await svc.list_open()
        assert any(r.id == row.id for r in open_rows)


@pytest.mark.asyncio
async def test_trip_project_creation(require_db):
    factory = get_session_factory()
    async with factory() as session:
        trip = await TripService(session, "owner").create_trip(
            "Test trip",
            [{"destination": "Tokyo"}, {"destination": "Dubai"}],
        )
        await session.commit()
        legs = await TripService(session, "owner").list_legs(trip.id)
        assert len(legs) == 2


@pytest.mark.asyncio
async def test_draft_versions(require_db):
    factory = get_session_factory()
    async with factory() as session:
        draft = await DraftService(session, "owner").save("Note", "Hello world")
        updated = await DraftService(session, "owner").rewrite(draft.id, "Hello world v2")
        await session.commit()
        assert updated is not None
        assert updated.current_version == 2


@pytest.mark.asyncio
async def test_deck_build_from_sources(require_db):
    factory = get_session_factory()
    async with factory() as session:
        deck = await DeckService(session, "owner").build_from_sources(
            "Test deck", "local-first AI", slide_count=4
        )
        await session.commit()
        slides = await DeckService(session, "owner").list_slides(deck.id)
        assert len(slides) >= 1


@pytest.mark.asyncio
async def test_ops_runbook_brief(require_db):
    factory = get_session_factory()
    async with factory() as session:
        await seed_agent_phase_data(session, "owner")
        await session.commit()
        brief = await OpsRunbookService(session, "owner").runbook_brief()
        assert brief["vendor_count"] >= 1


def test_phase_tools_registered_phases_3_9(client, require_db):
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    agents = {a["type"]: a for a in res.json()}
    assert "unified_search" in agents["knowledge_librarian"]["phase"]["tools"]
    assert "update_request_status" in agents["concierge"]["phase"]["tools"]
    assert "create_trip_project" in agents["travel"]["phase"]["tools"]
    assert "luxury_desk_trends" in agents["luxury_analyst"]["phase"]["tools"]
    assert "rewrite_draft" in agents["writing"]["phase"]["tools"]
    assert "build_deck_from_sources" in agents["presentation"]["phase"]["tools"]
    assert "ops_runbook_brief" in agents["operations"]["phase"]["tools"]
