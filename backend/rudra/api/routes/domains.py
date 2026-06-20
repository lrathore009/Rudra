"""Domain phase API routes — HUD data for phases 3–9."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.core.database import get_db
from rudra.domains.concierge import ExperienceService
from rudra.domains.librarian import LibrarianRetrievalService
from rudra.domains.luxury_desk import LuxuryDeskService
from rudra.domains.operations import OpsRunbookService
from rudra.domains.presentation import DeckService
from rudra.domains.travel import TripService
from rudra.domains.writing import DraftService
from rudra.knowledge.luxury import LuxuryCategory

router = APIRouter(prefix="/domains", tags=["domains"])


class ConciergeRequestBody(BaseModel):
    title: str
    details: str
    venue: str | None = None
    party_size: int | None = None
    scheduled_at: str | None = None


class TripCreateBody(BaseModel):
    title: str
    destinations: list[str]


class LibrarianQuery(BaseModel):
    query: str
    limit: int = 8


class DraftBody(BaseModel):
    title: str
    content: str
    format: str = "email"
    tone: str | None = None


class DeckBuildBody(BaseModel):
    title: str
    query: str
    slides: int = 6
    audience: str = "executive"


@router.get("/librarian/traces")
async def librarian_traces(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    traces = await LibrarianRetrievalService(db, user_id).recent_traces(limit=10)
    return [
        {
            "id": str(t.id),
            "query": t.query[:120],
            "latency_ms": t.latency_ms,
            "source_count": len(t.sources or []),
        }
        for t in traces
    ]


@router.post("/librarian/search")
async def librarian_search(
    body: LibrarianQuery,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    hits = await LibrarianRetrievalService(db, user_id).unified_search(body.query, limit=body.limit)
    return hits


@router.post("/librarian/answer")
async def librarian_answer_route(
    body: LibrarianQuery,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await LibrarianRetrievalService(db, user_id).answer(body.query, limit=body.limit)


@router.get("/concierge/requests")
async def list_concierge_requests(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ExperienceService(db, user_id)
    open_rows = await svc.list_open()
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "status": r.status,
            "venue_name": r.venue_name,
            "scheduled_at": r.scheduled_at,
        }
        for r in open_rows
    ]


@router.post("/concierge/requests")
async def create_concierge_request(
    body: ConciergeRequestBody,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    row = await ExperienceService(db, user_id).log_request(
        body.title,
        body.details,
        venue_name=body.venue,
        party_size=body.party_size,
        scheduled_at=body.scheduled_at,
    )
    return {"id": str(row.id), "title": row.title, "status": row.status}


@router.get("/travel/trips")
async def list_trips(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    trips = await TripService(db, user_id).list_trips()
    out = []
    for t in trips:
        legs = await TripService(db, user_id).list_legs(t.id)
        out.append(
            {
                "id": str(t.id),
                "title": t.title,
                "status": t.status,
                "legs": [{"destination": leg.destination, "status": leg.status} for leg in legs],
            }
        )
    return out


@router.post("/travel/trips")
async def create_trip(
    body: TripCreateBody,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    legs = [{"destination": d} for d in body.destinations]
    trip = await TripService(db, user_id).create_trip(body.title, legs)
    return {"id": str(trip.id), "title": trip.title}


@router.get("/luxury/desk")
async def luxury_desk(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    svc = LuxuryDeskService(db, user_id)
    trends = await svc.desk_trends()
    snapshots = await svc.list_snapshots(limit=5)
    alerts = await svc.list_alerts()
    return {
        "trends": trends,
        "snapshots": [
            {"subject": s.subject, "category": s.category, "exclusivity": s.exclusivity_score}
            for s in snapshots
        ],
        "alerts": [{"title": a.watchlist_title, "type": a.alert_type} for a in alerts],
    }


@router.get("/writing/drafts")
async def list_drafts(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    drafts = await DraftService(db, user_id).list_drafts(limit=12)
    return [
        {"id": str(d.id), "title": d.title, "status": d.status, "version": d.current_version}
        for d in drafts
    ]


@router.post("/writing/drafts")
async def save_draft_route(
    body: DraftBody,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    draft = await DraftService(db, user_id).save(body.title, body.content, fmt=body.format, tone=body.tone)
    return {"id": str(draft.id), "title": draft.title}


@router.get("/presentation/decks")
async def list_decks(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    decks = await DeckService(db, user_id).list_decks()
    return [
        {"id": str(d.id), "title": d.title, "slides": d.slide_count, "status": d.status}
        for d in decks
    ]


@router.post("/presentation/decks/build")
async def build_deck(
    body: DeckBuildBody,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    deck = await DeckService(db, user_id).build_from_sources(
        body.title, body.query, audience=body.audience, slide_count=body.slides
    )
    return {"id": str(deck.id), "title": deck.title, "slides": deck.slide_count}


@router.get("/presentation/decks/{deck_id}")
async def get_deck(
    deck_id: UUID,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = DeckService(db, user_id)
    deck = await svc.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    slides = await svc.list_slides(deck_id)
    return {
        "id": str(deck.id),
        "title": deck.title,
        "slides": [
            {"sequence": s.sequence, "title": s.title, "content": s.content[:400], "notes": s.speaker_notes}
            for s in slides
        ],
    }


@router.get("/operations/runbook")
async def ops_runbook(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return await OpsRunbookService(db, user_id).runbook_brief()
