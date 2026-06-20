"""#18 — Federated memory sync across devices."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.jarvis.events import EventType, get_event_bus
from rudra.jarvis.models import FederationDevice
from rudra.memory.models.memory import Memory
from rudra.memory.service import MemoryService


async def register_device(
    session: AsyncSession,
    user_id: str,
    device_label: str,
) -> dict[str, str]:
    device_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(32)
    session.add(
        FederationDevice(
            user_id=user_id,
            device_id=device_id,
            device_label=device_label,
            sync_token=token,
        )
    )
    await session.flush()
    return {"device_id": device_id, "sync_token": token}


async def export_memories(session: AsyncSession, user_id: str, sync_token: str) -> list[dict[str, Any]]:
    dev = await _auth_device(session, user_id, sync_token)
    if not dev:
        raise ValueError("Invalid sync token")
    svc = MemoryService(session, user_id)
    recent = await svc.list_recent(limit=200)
    payload = [
        {
            "title": m.title,
            "content": m.content,
            "memory_type": m.memory_type,
            "importance": m.importance,
            "source": m.source,
        }
        for m in recent
    ]
    from rudra.research.reports import ResearchReportService

    research = await ResearchReportService(session, user_id).export_for_federation(limit=50)
    for item in research:
        item["type"] = "research_report"
    payload.extend(research)

    from rudra.domains.concierge import ExperienceService
    from rudra.domains.librarian import LibrarianRetrievalService
    from rudra.domains.luxury_desk import LuxuryDeskService
    from rudra.domains.operations import OpsRunbookService
    from rudra.domains.presentation import DeckService
    from rudra.domains.travel import TripService
    from rudra.domains.writing import DraftService

    for exporter in (
        LibrarianRetrievalService(session, user_id).export_for_federation,
        ExperienceService(session, user_id).export_for_federation,
        TripService(session, user_id).export_for_federation,
        LuxuryDeskService(session, user_id).export_for_federation,
        DraftService(session, user_id).export_for_federation,
        DeckService(session, user_id).export_for_federation,
        OpsRunbookService(session, user_id).export_for_federation,
    ):
        payload.extend(await exporter(limit=20))
    dev.last_sync_at = datetime.now(timezone.utc).isoformat()
    get_event_bus().publish(EventType.SYNC_COMPLETE, {"device_id": dev.device_id, "count": len(payload)})
    return payload


async def import_memories(
    session: AsyncSession,
    user_id: str,
    sync_token: str,
    items: list[dict[str, Any]],
) -> int:
    dev = await _auth_device(session, user_id, sync_token)
    if not dev:
        raise ValueError("Invalid sync token")
    from rudra.memory.models.memory import MemoryType

    svc = MemoryService(session, user_id)
    count = 0
    for item in items[:100]:
        if item.get("type") in (
            "research_report",
            "retrieval_trace",
            "concierge_request",
            "travel_trip",
            "luxury_snapshot",
            "writing_draft",
            "presentation_deck",
            "ops_vendor",
        ):
            continue
        mt = MemoryType(item.get("memory_type", "semantic"))
        await svc.create(
            mt,
            title=str(item.get("title", "Synced memory"))[:512],
            content=str(item.get("content", ""))[:8000],
            importance=float(item.get("importance", 0.5)),
            source=f"federation:{dev.device_label}",
        )
        count += 1
    research_items = [i for i in items if i.get("type") == "research_report"]
    if research_items:
        from rudra.research.reports import ResearchReportService

        count += await ResearchReportService(session, user_id).import_from_federation(research_items)
    dev.last_sync_at = datetime.now(timezone.utc).isoformat()
    get_event_bus().publish(EventType.SYNC_COMPLETE, {"device_id": dev.device_id, "imported": count})
    return count


async def _auth_device(session: AsyncSession, user_id: str, sync_token: str) -> FederationDevice | None:
    result = await session.execute(
        select(FederationDevice).where(
            FederationDevice.user_id == user_id,
            FederationDevice.sync_token == sync_token,
        )
    )
    return result.scalar_one_or_none()
