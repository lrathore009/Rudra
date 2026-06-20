"""#3 — Continuous operators with persisted state."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.autonomy.scheduler import Job, get_scheduler
from rudra.core.config import get_settings
from rudra.core.logging import get_logger
from rudra.jarvis.events import EventType, get_event_bus
from rudra.jarvis.models import OperatorState

logger = get_logger(__name__)

BUILTIN_OPERATORS: list[dict[str, Any]] = [
    {
        "id": "monitor_projects",
        "name": "Project Monitor",
        "interval_seconds": 3600,
        "description": "Alert on stale/blocked founder projects",
    },
    {
        "id": "monitor_inbox",
        "name": "Inbox Monitor",
        "interval_seconds": 1800,
        "description": "Flag emails needing attention",
    },
    {
        "id": "morning_digest_spoken",
        "name": "Spoken Morning Digest",
        "daily_at": None,
        "description": "Jarvis persona + TTS briefing",
    },
    {
        "id": "monitor_research_watchlist",
        "name": "Research Watchlist Monitor",
        "interval_seconds": 21600,
        "description": "Refresh stale watchlist topics in research library",
    },
    {
        "id": "research_digest_spoken",
        "name": "Spoken Research Brief",
        "interval_seconds": 86400,
        "description": "Jarvis research library spoken summary",
    },
    {
        "id": "monitor_concierge_requests",
        "name": "Concierge Request Monitor",
        "interval_seconds": 7200,
        "description": "Flag stale open concierge requests",
    },
    {
        "id": "monitor_luxury_watchlist",
        "name": "Luxury Watchlist Monitor",
        "interval_seconds": 43200,
        "description": "Refresh luxury desk alerts",
    },
    {
        "id": "monitor_upcoming_legs",
        "name": "Travel Leg Monitor",
        "interval_seconds": 21600,
        "description": "Track upcoming trip legs",
    },
    {
        "id": "monitor_maintenance_due",
        "name": "Maintenance Due Monitor",
        "interval_seconds": 86400,
        "description": "Sync maintenance SLA events",
    },
]


@dataclass
class OperatorManifest:
    id: str
    name: str
    interval_seconds: int | None = None
    daily_at: str | None = None
    enabled: bool = True


async def load_operator_state(session: AsyncSession, user_id: str, operator_id: str) -> dict:
    result = await session.execute(
        select(OperatorState).where(
            OperatorState.user_id == user_id,
            OperatorState.operator_id == operator_id,
        )
    )
    row = result.scalar_one_or_none()
    return row.state if row and row.state else {}


async def save_operator_state(
    session: AsyncSession,
    user_id: str,
    operator_id: str,
    state: dict,
) -> None:
    result = await session.execute(
        select(OperatorState).where(
            OperatorState.user_id == user_id,
            OperatorState.operator_id == operator_id,
        )
    )
    row = result.scalar_one_or_none()
    payload = {**state, "last_tick": time.time()}
    if row:
        row.state = payload
        row.last_tick = str(time.time())
    else:
        session.add(
            OperatorState(
                user_id=user_id,
                operator_id=operator_id,
                state=payload,
                last_tick=str(time.time()),
            )
        )
    await session.flush()


async def tick_monitor_projects() -> str:
    from rudra.core.database import get_session_factory
    from rudra.projects.service import ProjectService

    factory = get_session_factory()
    async with factory() as db:
        svc = ProjectService(db, "owner")
        stale = await svc.intelligence.identify_stale()
        blocked = await svc.intelligence.identify_blocked()
        state = {
            "stale": [p.name for p in stale[:5]],
            "blocked": [p.name for p in blocked[:5]],
        }
        await save_operator_state(db, "owner", "monitor_projects", state)
        await db.commit()
        get_event_bus().publish(EventType.OPERATOR_TICK, {"operator": "monitor_projects", **state})
        return json.dumps(state)


async def tick_monitor_inbox() -> str:
    from rudra.core.database import get_session_factory
    from rudra.jarvis.connectors.registry import ConnectorHub

    factory = get_session_factory()
    async with factory() as db:
        hub = ConnectorHub(db, "owner")
        emails = await hub.recent_emails(limit=10)
        attention = [f"{e.sender}: {e.subject}" for e in emails if e.needs_attention]
        state = {"attention": attention}
        await save_operator_state(db, "owner", "monitor_inbox", state)
        await db.commit()
        get_event_bus().publish(EventType.OPERATOR_TICK, {"operator": "monitor_inbox", **state})
        return json.dumps(state)


async def tick_spoken_digest() -> str:
    from rudra.core.database import get_session_factory
    from rudra.jarvis.digest import synthesize_spoken_digest

    factory = get_session_factory()
    async with factory() as db:
        result = await synthesize_spoken_digest(db, "owner")
        await save_operator_state(db, "owner", "morning_digest_spoken", {"chars": len(result["text"])})
        await db.commit()
        return result["text"][:500]


async def tick_research_watchlist() -> str:
    from rudra.core.database import get_session_factory
    from rudra.research.pipeline import research_with_library
    from rudra.research.reports import ResearchReportService

    factory = get_session_factory()
    async with factory() as db:
        svc = ResearchReportService(db, "owner")
        watchlist = await svc.list_watchlist()
        refreshed: list[str] = []
        for item in watchlist[:5]:
            await research_with_library(db, "owner", item.query_template, force_refresh=True)
            refreshed.append(item.topic)
        state = {"refreshed": refreshed}
        await save_operator_state(db, "owner", "monitor_research_watchlist", state)
        await db.commit()
        get_event_bus().publish(EventType.OPERATOR_TICK, {"operator": "monitor_research_watchlist", **state})
        return json.dumps(state)


async def tick_research_spoken() -> str:
    from rudra.core.database import get_session_factory
    from rudra.jarvis.research_digest import synthesize_spoken_research_brief

    factory = get_session_factory()
    async with factory() as db:
        result = await synthesize_spoken_research_brief(db, "owner")
        await save_operator_state(db, "owner", "research_digest_spoken", {"chars": len(result["text"])})
        await db.commit()
        return result["text"][:500]


async def tick_concierge_requests() -> str:
    from rudra.core.database import get_session_factory
    from rudra.domains.concierge import ExperienceService

    factory = get_session_factory()
    async with factory() as db:
        stale = await ExperienceService(db, "owner").stale_requests()
        state = {"stale": [r.title for r in stale[:5]]}
        await save_operator_state(db, "owner", "monitor_concierge_requests", state)
        await db.commit()
        return json.dumps(state)


async def tick_luxury_watchlist() -> str:
    from rudra.core.database import get_session_factory
    from rudra.domains.luxury_desk import LuxuryDeskService

    factory = get_session_factory()
    async with factory() as db:
        triggered = await LuxuryDeskService(db, "owner").monitor_watchlist()
        state = {"triggered": triggered}
        await save_operator_state(db, "owner", "monitor_luxury_watchlist", state)
        await db.commit()
        return json.dumps(state)


async def tick_upcoming_legs() -> str:
    from rudra.core.database import get_session_factory
    from rudra.domains.travel import TripService

    factory = get_session_factory()
    async with factory() as db:
        legs = await TripService(db, "owner").upcoming_legs(limit=5)
        state = {"legs": [leg.destination for leg in legs]}
        await save_operator_state(db, "owner", "monitor_upcoming_legs", state)
        await db.commit()
        return json.dumps(state)


async def tick_maintenance_due() -> str:
    from rudra.core.database import get_session_factory
    from rudra.domains.operations import OpsRunbookService

    factory = get_session_factory()
    async with factory() as db:
        count = await OpsRunbookService(db, "owner").sync_maintenance_sla()
        state = {"synced": count}
        await save_operator_state(db, "owner", "monitor_maintenance_due", state)
        await db.commit()
        return json.dumps(state)


def register_operators() -> None:
    if not get_settings().enable_operators:
        return
    sched = get_scheduler()
    if sched.get("monitor_projects") is None:
        sched.add_job(
            Job(
                id="monitor_projects",
                name="Project Monitor",
                fn=tick_monitor_projects,
                interval_seconds=3600,
            )
        )
    if sched.get("monitor_inbox") is None:
        sched.add_job(
            Job(
                id="monitor_inbox",
                name="Inbox Monitor",
                fn=tick_monitor_inbox,
                interval_seconds=1800,
            )
        )
    if sched.get("morning_digest_spoken") is None:
        sched.add_job(
            Job(
                id="morning_digest_spoken",
                name="Spoken Morning Digest",
                fn=tick_spoken_digest,
                daily_at=get_settings().morning_digest_time,
            )
        )
    if sched.get("monitor_research_watchlist") is None:
        sched.add_job(
            Job(
                id="monitor_research_watchlist",
                name="Research Watchlist Monitor",
                fn=tick_research_watchlist,
                interval_seconds=21600,
            )
        )
    if sched.get("research_digest_spoken") is None:
        sched.add_job(
            Job(
                id="research_digest_spoken",
                name="Spoken Research Brief",
                fn=tick_research_spoken,
                interval_seconds=86400,
            )
        )
    for op_id, name, fn, interval in (
        ("monitor_concierge_requests", "Concierge Monitor", tick_concierge_requests, 7200),
        ("monitor_luxury_watchlist", "Luxury Monitor", tick_luxury_watchlist, 43200),
        ("monitor_upcoming_legs", "Travel Monitor", tick_upcoming_legs, 21600),
        ("monitor_maintenance_due", "Maintenance Monitor", tick_maintenance_due, 86400),
    ):
        if sched.get(op_id) is None:
            sched.add_job(Job(id=op_id, name=name, fn=fn, interval_seconds=interval))
    logger.info("operators_registered")
