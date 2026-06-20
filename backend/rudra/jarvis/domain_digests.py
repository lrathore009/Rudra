"""Jarvis spoken briefs for agent phases 3–9."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from rudra.brain.orchestrator import Brain, Message
from rudra.jarvis.events import EventType, get_event_bus
from rudra.jarvis.persona import jarvis_system_prompt
from rudra.jarvis.tts import synthesize_speech
from rudra.domains.concierge import ExperienceService
from rudra.domains.librarian import LibrarianRetrievalService
from rudra.domains.luxury_desk import LuxuryDeskService
from rudra.domains.operations import OpsRunbookService
from rudra.domains.travel import TripService
from rudra.domains.writing import DraftService
from rudra.domains.presentation import DeckService


async def _spoken(session: AsyncSession, user_id: str, mode: str, raw: str) -> dict:
    brain = Brain()
    result = await brain.think(
        [Message(role="user", content=f"Synthesize a concise spoken briefing:\n\n{raw}")],
        system=jarvis_system_prompt(mode=mode),
        model_tier="fast",
    )
    audio = await synthesize_speech(result.content)
    get_event_bus().publish(EventType.RESEARCH_COMPLETED, {"user_id": user_id, "spoken": True, "mode": mode})
    return {"text": result.content, "sources_preview": raw[:1500], "audio": audio}


async def spoken_librarian_brief(session: AsyncSession, user_id: str, query: str | None = None) -> dict:
    svc = LibrarianRetrievalService(session, user_id)
    if query:
        result = await svc.answer(query)
        raw = result["answer"]
    else:
        traces = await svc.recent_traces(limit=3)
        raw = "Recent retrieval activity:\n" + "\n".join(f"- {t.query[:80]}" for t in traces)
    return await _spoken(session, user_id, "research", raw)


async def spoken_concierge_brief(session: AsyncSession, user_id: str) -> dict:
    svc = ExperienceService(session, user_id)
    open_rows = await svc.list_open(limit=5)
    recs = await svc.recommend("dining")
    raw = "## Open requests\n" + "\n".join(f"- {r.title} ({r.status})" for r in open_rows)
    raw += "\n\n## Preferences\n" + "\n".join(f"- {r['value']}" for r in recs[:3])
    return await _spoken(session, user_id, "concierge", raw)


async def spoken_travel_brief(session: AsyncSession, user_id: str) -> dict:
    brief = await TripService(session, user_id).travel_brief()
    raw = str(brief)
    return await _spoken(session, user_id, "travel", raw)


async def spoken_luxury_brief(session: AsyncSession, user_id: str) -> dict:
    trends = await LuxuryDeskService(session, user_id).desk_trends()
    raw = f"Luxury desk: {trends['count']} snapshots, exclusivity {trends['avg_exclusivity']}, watchlist {trends['watchlist_count']}"
    return await _spoken(session, user_id, "luxury", raw)


async def spoken_writing_brief(session: AsyncSession, user_id: str) -> dict:
    drafts = await DraftService(session, user_id).list_drafts(limit=5)
    raw = "Draft queue:\n" + "\n".join(f"- {d.title} ({d.status})" for d in drafts)
    return await _spoken(session, user_id, "writing", raw)


async def spoken_deck_brief(session: AsyncSession, user_id: str) -> dict:
    decks = await DeckService(session, user_id).list_decks(limit=5)
    raw = "Decks:\n" + "\n".join(f"- {d.title} ({d.slide_count} slides)" for d in decks)
    return await _spoken(session, user_id, "presentation", raw)


async def spoken_ops_brief(session: AsyncSession, user_id: str) -> dict:
    brief = await OpsRunbookService(session, user_id).runbook_brief()
    raw = str(brief)
    return await _spoken(session, user_id, "operations", raw)
