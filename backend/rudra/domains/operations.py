"""Operations runbook — vendors, SLA events, maintenance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.domains.models import OpsSlaEvent, VendorInteraction
from rudra.graph.service import GraphService
from rudra.projects.service import ProjectService


class OpsRunbookService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def log_vendor_interaction(
        self,
        vendor_name: str,
        notes: str,
        *,
        interaction_type: str = "contact",
    ) -> VendorInteraction:
        row = VendorInteraction(
            user_id=self.user_id,
            vendor_name=vendor_name,
            interaction_type=interaction_type,
            notes=notes,
        )
        self.session.add(row)
        await self.session.flush()
        graph = GraphService(self.session, self.user_id)
        await graph.get_or_create_entity(vendor_name, "company")
        return row

    async def create_sla_event(
        self,
        vendor_name: str,
        event_type: str,
        *,
        due_at: str | None = None,
    ) -> OpsSlaEvent:
        row = OpsSlaEvent(
            user_id=self.user_id,
            vendor_name=vendor_name,
            event_type=event_type,
            due_at=due_at,
            status="open",
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_sla_events(self, *, status: str | None = "open", limit: int = 20) -> list[OpsSlaEvent]:
        stmt = (
            select(OpsSlaEvent)
            .where(OpsSlaEvent.user_id == self.user_id)
            .order_by(OpsSlaEvent.created_at.desc())
            .limit(limit)
        )
        if status:
            stmt = stmt.where(OpsSlaEvent.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_interactions(self, *, limit: int = 20) -> list[VendorInteraction]:
        result = await self.session.execute(
            select(VendorInteraction)
            .where(VendorInteraction.user_id == self.user_id)
            .order_by(VendorInteraction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def maintenance_due(self) -> list[dict[str, Any]]:
        data = AgentDataService(self.session, self.user_id)
        items = await data.list_artifacts(AgentType.OPERATIONS, artifact_type="maintenance", limit=30)
        due = []
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        for item in items:
            meta = item.metadata_ or {}
            next_due = meta.get("next_due", "")
            if next_due and next_due <= today:
                due.append(
                    {
                        "title": item.title,
                        "next_due": next_due,
                        "status": item.status,
                        "content": item.content[:120],
                    }
                )
        return due

    async def runbook_brief(self) -> dict[str, Any]:
        data = AgentDataService(self.session, self.user_id)
        vendors = await data.list_artifacts(AgentType.OPERATIONS, artifact_type="vendor", limit=10)
        maintenance = await self.maintenance_due()
        sla = await self.list_sla_events(limit=10)
        return {
            "vendor_count": len(vendors),
            "maintenance_due": maintenance,
            "open_sla": [
                {"vendor": e.vendor_name, "type": e.event_type, "due_at": e.due_at} for e in sla
            ],
        }

    async def escalate(self, vendor_name: str, issue: str) -> OpsSlaEvent:
        projects = ProjectService(self.session, self.user_id)
        project = await projects.get_by_name("Household Operations")
        if project is None:
            project = await projects.create_project(
                {
                    "name": "Household Operations",
                    "description": "Personal operations runbook",
                    "status": "active",
                    "priority": 3,
                    "category": "operations",
                }
            )
        await projects.create_task(
            project.id,
            {
                "title": f"Escalation: {vendor_name}",
                "description": issue,
                "status": "todo",
                "priority": 1,
            },
        )
        return await self.create_sla_event(vendor_name, "escalation", due_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    async def sync_maintenance_sla(self) -> int:
        due = await self.maintenance_due()
        count = 0
        for item in due:
            await self.create_sla_event(item["title"], "maintenance_due", due_at=item.get("next_due"))
            count += 1
        return count

    async def export_for_federation(self, *, limit: int = 30) -> list[dict[str, Any]]:
        vendors = AgentDataService(self.session, self.user_id)
        roster = await vendors.list_artifacts(AgentType.OPERATIONS, artifact_type="vendor", limit=limit)
        return [
            {
                "type": "ops_vendor",
                "title": v.title,
                "content": v.content[:500],
            }
            for v in roster
        ]
