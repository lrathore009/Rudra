"""Integration and daily briefing services."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.integrations.executive import ExecutiveCommandService
from rudra.integrations.models import DailyBriefing, ExternalEmail, ExternalEvent, Integration
from rudra.integrations.providers import CalendarEvent, EmailMessage, MockCalendarProvider, MockEmailProvider
from rudra.jarvis.connectors.registry import ConnectorHub
from rudra.projects.service import ProjectService


class IntegrationService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.executive = ExecutiveCommandService(session, user_id)
        self.hub = ConnectorHub(session, user_id)
        self.calendar = MockCalendarProvider()
        self.email = MockEmailProvider()

    async def list_integrations(self) -> list[dict]:
        return await self.executive.list_connector_status()

    async def connect_mock(self) -> Integration:
        await self.executive.connect_mock_stack()
        result = await self.session.execute(
            select(Integration).where(
                Integration.user_id == self.user_id,
                Integration.provider == "mock_local",
            )
        )
        row = result.scalar_one_or_none()
        if row:
            return row
        integration = Integration(user_id=self.user_id, provider="mock_local", status="connected")
        self.session.add(integration)
        await self.session.flush()
        return integration

    async def calendar_events(self) -> list[ExternalEvent]:
        live = await self.hub.calendar_events()
        if not live:
            live = await self.calendar.list_events(self.user_id)
        return [
            ExternalEvent(
                user_id=self.user_id,
                provider=e.provider,
                title=e.title,
                starts_at=e.starts_at,
                ends_at=e.ends_at,
                location=e.location,
            )
            for e in live
        ]

    async def recent_emails(self, *, limit: int = 10) -> list[ExternalEmail]:
        live = await self.hub.recent_emails(limit=limit)
        if not live:
            live = await self.email.list_recent(self.user_id, limit=limit)
        return [
            ExternalEmail(
                user_id=self.user_id,
                provider=e.provider,
                sender=e.sender,
                subject=e.subject,
                snippet=e.snippet,
                received_at=e.received_at,
                needs_attention=e.needs_attention,
            )
            for e in live
        ]


class BriefingService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.executive = ExecutiveCommandService(session, user_id)
        self.projects = ProjectService(session, user_id)

    async def generate_daily(self) -> DailyBriefing:
        today = datetime.now().strftime("%Y-%m-%d")
        stack = await self.executive.get_command_stack()
        lines = [f"# Daily Command Briefing — {today}", ""]

        weather = stack["tier2"].get("weather")
        if weather:
            lines.extend(
                [
                    "## Weather",
                    f"- {weather['location']}: {weather['summary']}"
                    + (f" ({weather['temp_c']}°C)" if weather.get("temp_c") is not None else ""),
                    "",
                ]
            )

        lines.append("## Today's meetings")
        for event in stack["tier1"]["calendar"][:5]:
            loc = f" @ {event['location']}" if event.get("location") else ""
            lines.append(f"- {event.get('starts_at')} · {event.get('title')}{loc}")

        lines.extend(["", "## Emails needing attention"])
        attention = [e for e in stack["tier1"]["email"] if e.get("needs_attention")]
        if attention:
            for mail in attention[:5]:
                lines.append(f"- {mail.get('sender')}: {mail.get('subject')}")
        else:
            lines.append("- None flagged")

        lines.extend(["", "## Open commitments"])
        for c in stack["commitments"][:5]:
            due = f" (due {c['due_at']})" if c.get("due_at") else ""
            lines.append(f"- {c['title']}{due}")

        lines.extend(["", "## Tasks"])
        for task in stack["tier1"]["tasks"][:5]:
            lines.append(f"- [{task.get('status')}] {task.get('title')}")

        lines.extend(["", "## Project focus"])
        for card in stack["projects"]["projects"][:5]:
            lines.append(f"- {card['name']} ({card['progress_percent']}%): {card['next_action']}")

        news = stack["tier2"].get("news") or []
        if news:
            lines.extend(["", "## Headlines"])
            for item in news[:3]:
                lines.append(f"- {item.get('title')} ({item.get('source', 'news')})")

        finance = stack["tier2"].get("finance") or []
        if finance:
            lines.extend(["", "## Finance pulse"])
            for line in finance[:4]:
                lines.append(f"- {line.get('label')}: {line.get('amount')} {line.get('currency', 'USD')}")

        travel = stack["tier3"].get("travel") or []
        if travel:
            lines.extend(["", "## Travel"])
            for t in travel[:3]:
                lines.append(f"- {t.get('title')}")

        health = stack["tier4"].get("health") or []
        if health:
            lines.extend(["", "## Recovery"])
            for h in health[:3]:
                lines.append(f"- {h.get('metric_type')}: {h.get('value')} {h.get('unit') or ''}")

        lines.extend(["", "## Suggested deep work block", "- 09:00–11:00 · highest-priority build"])

        from rudra.research.reports import ResearchReportService

        library = ResearchReportService(self.session, self.user_id)
        trends = await library.trends()
        if trends["count"]:
            lines.extend(
                [
                    "",
                    "## Research library",
                    f"- {trends['count']} reports · avg confidence {trends['avg_confidence']:.2f} · stale {trends['stale_count']}",
                ]
            )
            recent = await library.list_recent(limit=3)
            for r in recent:
                lines.append(f"- {r.title} (conf {r.confidence_score:.2f})")

        from rudra.domains.concierge import ExperienceService

        open_cg = await ExperienceService(self.session, self.user_id).list_open(limit=3)
        if open_cg:
            lines.extend(["", "## Concierge requests"])
            for r in open_cg:
                lines.append(f"- [{r.status}] {r.title}")

        from rudra.domains.travel import TripService

        travel = await TripService(self.session, self.user_id).travel_brief()
        if travel["upcoming_legs"]:
            lines.extend(["", "## Upcoming travel"])
            for leg in travel["upcoming_legs"][:3]:
                lines.append(f"- {leg['destination']} @ {leg.get('starts_at', 'TBD')}")

        from rudra.domains.operations import OpsRunbookService

        ops = await OpsRunbookService(self.session, self.user_id).runbook_brief()
        if ops["maintenance_due"]:
            lines.extend(["", "## Ops maintenance due"])
            for m in ops["maintenance_due"][:3]:
                lines.append(f"- {m['title']} (due {m['next_due']})")

        content = "\n".join(lines)
        briefing = DailyBriefing(
            user_id=self.user_id,
            briefing_date=today,
            content=content,
            metadata_={"tiers": list(stack.keys())},
        )
        self.session.add(briefing)
        await self.session.flush()
        return briefing

    async def get_latest(self) -> DailyBriefing | None:
        result = await self.session.execute(
            select(DailyBriefing)
            .where(DailyBriefing.user_id == self.user_id)
            .order_by(DailyBriefing.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()
