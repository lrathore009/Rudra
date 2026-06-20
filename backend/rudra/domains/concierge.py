"""Experience concierge service — requests, recommendations, venue linking."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.domains.models import ConciergeRequest
from rudra.graph.service import GraphService


class ExperienceService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.data = AgentDataService(session, user_id)

    async def log_request(
        self,
        title: str,
        details: str,
        *,
        venue_name: str | None = None,
        party_size: int | None = None,
        scheduled_at: str | None = None,
        status: str = "requested",
    ) -> ConciergeRequest:
        row = ConciergeRequest(
            user_id=self.user_id,
            title=title,
            details=details,
            venue_name=venue_name,
            party_size=party_size,
            scheduled_at=scheduled_at,
            status=status,
        )
        self.session.add(row)
        await self.session.flush()
        await self.data.create_artifact(
            AgentType.CONCIERGE,
            "experience_request",
            title,
            details,
            metadata={"request_id": str(row.id), "venue": venue_name},
            status=status,
        )
        return row

    async def update_status(self, request_id: uuid.UUID, status: str) -> ConciergeRequest | None:
        row = await self.get(request_id)
        if not row:
            return None
        row.status = status
        await self.session.flush()
        return row

    async def get(self, request_id: uuid.UUID) -> ConciergeRequest | None:
        result = await self.session.execute(
            select(ConciergeRequest).where(
                ConciergeRequest.id == request_id,
                ConciergeRequest.user_id == self.user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_open(self, *, limit: int = 20) -> list[ConciergeRequest]:
        result = await self.session.execute(
            select(ConciergeRequest)
            .where(
                ConciergeRequest.user_id == self.user_id,
                ConciergeRequest.status.in_(("requested", "pending", "confirmed")),
            )
            .order_by(ConciergeRequest.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_recent(self, *, limit: int = 20) -> list[ConciergeRequest]:
        result = await self.session.execute(
            select(ConciergeRequest)
            .where(ConciergeRequest.user_id == self.user_id)
            .order_by(ConciergeRequest.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def recommend(self, category: str = "dining", *, limit: int = 3) -> list[dict[str, str]]:
        prefs = await self.data.list_preferences(category=category, limit=20)
        recs = []
        for p in prefs[:limit]:
            recs.append({"category": p.category, "preference": p.key, "value": p.value})
        if len(recs) < limit:
            dining = await self.data.list_preferences(category="hotels", limit=limit)
            for p in dining[: limit - len(recs)]:
                recs.append({"category": p.category, "preference": p.key, "value": p.value})
        return recs

    async def link_venue(self, request_id: uuid.UUID, venue_name: str) -> ConciergeRequest | None:
        row = await self.get(request_id)
        if not row:
            return None
        graph = GraphService(self.session, self.user_id)
        entity = await graph.get_or_create_entity(venue_name, "topic")
        row.venue_name = venue_name
        row.entity_id = entity.id
        await self.session.flush()
        return row

    async def stale_requests(self, *, hours: int = 48) -> list[ConciergeRequest]:
        from datetime import datetime, timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        open_rows = await self.list_open(limit=50)
        return [r for r in open_rows if r.created_at and r.created_at < cutoff]

    async def export_for_federation(self, *, limit: int = 50) -> list[dict[str, Any]]:
        rows = await self.list_recent(limit=limit)
        return [
            {
                "type": "concierge_request",
                "title": r.title,
                "details": r.details,
                "status": r.status,
                "venue_name": r.venue_name,
            }
            for r in rows
        ]
