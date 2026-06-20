"""Travel itinerary engine — trips, legs, project templates."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.domains.models import TravelLeg, TravelTrip
from rudra.graph.service import GraphService
from rudra.memory.service import MemoryService
from rudra.projects.service import ProjectService


DEFAULT_VISA_CHECKLIST = [
    "Check passport validity (6+ months)",
    "Confirm visa requirements",
    "Register travel apps (Visit Japan Web, etc.)",
    "Save embassy contact",
]


class TripService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def create_trip(
        self,
        title: str,
        legs: list[dict[str, Any]],
        *,
        create_project: bool = True,
    ) -> TravelTrip:
        project_id = None
        if create_project:
            projects = ProjectService(self.session, self.user_id)
            project = await projects.create_project(
                {
                    "name": title,
                    "description": "Travel itinerary project",
                    "status": "active",
                    "priority": 2,
                    "category": "travel",
                }
            )
            project_id = project.id
            for leg in legs:
                await projects.create_task(
                    project.id,
                    {
                        "title": f"Leg: {leg.get('destination', 'destination')}",
                        "description": leg.get("notes", ""),
                        "status": "todo",
                        "priority": 2,
                    },
                )

        trip = TravelTrip(
            user_id=self.user_id,
            title=title,
            status="planning",
            project_id=project_id,
            metadata_={"leg_count": len(legs)},
        )
        self.session.add(trip)
        await self.session.flush()

        graph = GraphService(self.session, self.user_id)
        for idx, leg in enumerate(legs, start=1):
            dest = str(leg.get("destination", ""))
            if dest:
                await graph.get_or_create_entity(dest, "topic")
            self.session.add(
                TravelLeg(
                    trip_id=trip.id,
                    user_id=self.user_id,
                    sequence=idx,
                    origin=leg.get("origin"),
                    destination=dest or f"Leg {idx}",
                    starts_at=leg.get("starts_at"),
                    ends_at=leg.get("ends_at"),
                    checklist=leg.get("checklist") or list(DEFAULT_VISA_CHECKLIST),
                    status="planned",
                    metadata_=leg.get("metadata"),
                )
            )
        await self.session.flush()

        data = AgentDataService(self.session, self.user_id)
        plan_text = "\n".join(
            f"Leg {i}: {leg.get('origin', '?')} → {leg.get('destination', '?')}" for i, leg in enumerate(legs, 1)
        )
        await data.create_artifact(
            AgentType.TRAVEL,
            "itinerary",
            title,
            plan_text,
            metadata={"trip_id": str(trip.id), "status": "planning"},
        )
        return trip

    async def get_trip(self, trip_id: uuid.UUID) -> TravelTrip | None:
        result = await self.session.execute(
            select(TravelTrip).where(TravelTrip.id == trip_id, TravelTrip.user_id == self.user_id)
        )
        return result.scalar_one_or_none()

    async def list_trips(self, *, limit: int = 10) -> list[TravelTrip]:
        result = await self.session.execute(
            select(TravelTrip)
            .where(TravelTrip.user_id == self.user_id)
            .order_by(TravelTrip.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_legs(self, trip_id: uuid.UUID) -> list[TravelLeg]:
        result = await self.session.execute(
            select(TravelLeg)
            .where(TravelLeg.trip_id == trip_id, TravelLeg.user_id == self.user_id)
            .order_by(TravelLeg.sequence)
        )
        return list(result.scalars().all())

    async def upcoming_legs(self, *, limit: int = 5) -> list[TravelLeg]:
        result = await self.session.execute(
            select(TravelLeg)
            .where(TravelLeg.user_id == self.user_id, TravelLeg.status.in_(("planned", "active")))
            .order_by(TravelLeg.starts_at.nulls_last())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def visa_requirements(self, destination: str, passport: str = "Indian") -> list[str]:
        dest = destination.lower()
        if "japan" in dest or "tokyo" in dest or "kyoto" in dest:
            return [
                f"{passport} passport: visa-free tourist entry 90 days (verify current rules)",
                "Register Visit Japan Web before arrival",
                *DEFAULT_VISA_CHECKLIST,
            ]
        if "dubai" in dest or "uae" in dest:
            return [
                f"{passport} passport: visa on arrival / e-visa (verify current rules)",
                *DEFAULT_VISA_CHECKLIST,
            ]
        return [f"Verify visa requirements for {destination} with {passport} passport", *DEFAULT_VISA_CHECKLIST]

    async def travel_brief(self) -> dict[str, Any]:
        trips = await self.list_trips(limit=3)
        legs = await self.upcoming_legs(limit=5)
        mem = MemoryService(self.session, self.user_id)
        travel_mem = await mem.search_by_tags(["travel", "visa", "itinerary"], limit=5)
        return {
            "trips": [{"id": str(t.id), "title": t.title, "status": t.status} for t in trips],
            "upcoming_legs": [
                {
                    "destination": leg.destination,
                    "starts_at": leg.starts_at,
                    "status": leg.status,
                }
                for leg in legs
            ],
            "memories": [m.title for m in travel_mem],
        }

    async def export_for_federation(self, *, limit: int = 20) -> list[dict[str, Any]]:
        trips = await self.list_trips(limit=limit)
        out = []
        for t in trips:
            legs = await self.list_legs(t.id)
            out.append(
                {
                    "type": "travel_trip",
                    "title": t.title,
                    "status": t.status,
                    "legs": [
                        {"destination": leg.destination, "starts_at": leg.starts_at} for leg in legs
                    ],
                }
            )
        return out
