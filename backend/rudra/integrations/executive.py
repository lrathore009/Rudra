"""Executive command stack — sync all tiers, build briefing context, import CSV."""

from __future__ import annotations

import csv
import io
import re
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.integrations.models import (
    EACommitment,
    EAFeedItem,
    EAFinanceSnapshot,
    EAHealthMetric,
    EATranscript,
    ExternalEmail,
    ExternalEvent,
    Integration,
)
from rudra.integrations.providers import (
    CalendarEvent,
    CommandFeedItem,
    ContactRecord,
    DocumentRef,
    EmailMessage,
    FinanceLine,
    HealthReading,
    MeetingTranscript,
    MockCalendarProvider,
    MockContactProvider,
    MockDocumentProvider,
    MockEmailProvider,
    MockFinanceProvider,
    MockHealthProvider,
    MockLuxuryProvider,
    MockSlackProvider,
    MockTaskProvider,
    MockTravelProvider,
    NewsHeadline,
    SlackMessage,
    TaskItem,
    TravelConfirmation,
    WeatherSnapshot,
)
from rudra.jarvis.connectors.registry import ConnectorHub
from rudra.projects.service import ProjectService

TRAVEL_PATTERNS = [
    re.compile(r"(booking confirmed|itinerary|reservation)", re.I),
    re.compile(r"(emirates|marriott|aman|four seasons|flight)", re.I),
]


class ExecutiveCommandService:
    """Phase 1 EA — unified command stack across all five tiers."""

    CONNECT_ORDER = [
        "google",
        "notion",
        "linear",
        "slack",
        "weather",
        "news",
        "microsoft",
        "mock_local",
    ]

    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.hub = ConnectorHub(session, user_id)

    async def list_connector_status(self) -> list[dict]:
        statuses = await self.hub.list_status()
        return [
            {
                "provider": s.provider,
                "connected": s.connected,
                "detail": s.detail,
                "tier": _tier_for_provider(s.provider),
            }
            for s in statuses
        ]

    async def connect_provider(self, provider: str, **credentials) -> dict:
        status = await self.hub.connect(provider, **credentials)
        if status.connected:
            await self._mark_integration(provider, "connected")
            await self.sync_all()
        return {"provider": status.provider, "connected": status.connected, "detail": status.detail}

    async def connect_mock_stack(self) -> dict:
        await self._mark_integration("mock_local", "connected")
        await self.sync_all()
        return {"status": "connected", "providers": len(self.CONNECT_ORDER)}

    async def sync_all(self) -> dict[str, int]:
        """Pull from all connectors and persist feed items + external rows."""
        counts: dict[str, int] = {}
        stack = await self._live_stack()
        counts["calendar"] = await self._sync_calendar(stack.get("calendar", []))
        counts["email"] = await self._sync_email(stack.get("email", []))
        counts["tasks"] = await self._sync_feed("task", stack.get("tasks", []))
        counts["contacts"] = await self._sync_feed("contact", stack.get("contacts", []))
        counts["documents"] = await self._sync_feed("document", stack.get("documents", []))
        counts["slack"] = await self._sync_feed("slack", stack.get("slack", []))
        counts["travel"] = await self._sync_feed("travel", stack.get("travel", []))
        counts["luxury"] = await self._sync_feed("luxury", stack.get("luxury", []))
        counts["news"] = await self._sync_feed("news", stack.get("news", []))
        counts["finance"] = await self._sync_finance(stack.get("finance", []))
        counts["health"] = await self._sync_health(stack.get("health", []))
        counts["knowledge"] = await self._sync_feed("knowledge", stack.get("knowledge", []))
        counts["commitments"] = await self._extract_commitments(stack)
        return counts

    async def get_command_stack(self) -> dict[str, Any]:
        """Full tier view for briefing + EA enrichment."""
        live = await self._live_stack()
        db_feed = await self._load_feed_by_category()
        projects = await ProjectService(self.session, self.user_id).dashboard()
        commitments = await self.list_commitments(limit=10)
        transcripts = await self.list_transcripts(limit=3)

        return {
            "tier1": {
                "calendar": live.get("calendar") or db_feed.get("calendar", []),
                "email": live.get("email") or db_feed.get("email", []),
                "tasks": live.get("tasks") or db_feed.get("task", []),
                "contacts": live.get("contacts") or db_feed.get("contact", []),
            },
            "tier2": {
                "weather": live.get("weather"),
                "news": live.get("news") or db_feed.get("news", []),
                "documents": live.get("documents") or db_feed.get("document", []),
                "finance": live.get("finance") or await self._finance_summary(),
            },
            "tier3": {
                "travel": live.get("travel") or db_feed.get("travel", []),
                "luxury": live.get("luxury") or db_feed.get("luxury", []),
            },
            "tier4": {
                "health": live.get("health") or await self._health_summary(),
                "family": db_feed.get("family", []),
            },
            "tier5": {
                "slack": live.get("slack") or db_feed.get("slack", []),
                "transcripts": transcripts,
                "voice_notes": db_feed.get("voice", []),
                "knowledge": live.get("knowledge") or db_feed.get("knowledge", []),
            },
            "projects": projects,
            "commitments": commitments,
            "connectors": await self.list_connector_status(),
        }

    async def list_commitments(self, *, limit: int = 20) -> list[dict]:
        result = await self.session.execute(
            select(EACommitment)
            .where(EACommitment.user_id == self.user_id, EACommitment.status == "open")
            .order_by(EACommitment.due_at.nulls_last())
            .limit(limit)
        )
        return [
            {
                "id": str(c.id),
                "title": c.title,
                "owner": c.owner,
                "due_at": c.due_at,
                "source_provider": c.source_provider,
            }
            for c in result.scalars().all()
        ]

    async def list_transcripts(self, *, limit: int = 5) -> list[dict]:
        result = await self.session.execute(
            select(EATranscript)
            .where(EATranscript.user_id == self.user_id)
            .order_by(EATranscript.created_at.desc())
            .limit(limit)
        )
        return [
            {
                "id": str(t.id),
                "title": t.title,
                "meeting_date": t.meeting_date,
                "action_items": t.action_items or [],
                "provider": t.provider,
            }
            for t in result.scalars().all()
        ]

    async def import_csv(self, kind: str, csv_text: str) -> dict[str, int]:
        reader = csv.DictReader(io.StringIO(csv_text))
        count = 0
        today = datetime.now().strftime("%Y-%m-%d")
        if kind == "finance":
            for row in reader:
                label = row.get("label") or row.get("name") or "Line"
                amount = float(row.get("amount", 0))
                self.session.add(
                    EAFinanceSnapshot(
                        user_id=self.user_id,
                        snapshot_date=row.get("date") or today,
                        label=label,
                        amount=amount,
                        currency=row.get("currency", "USD"),
                        category=row.get("category"),
                    )
                )
                count += 1
        elif kind == "crm":
            for row in reader:
                name = row.get("name") or "Contact"
                self.session.add(
                    EAFeedItem(
                        user_id=self.user_id,
                        category="contact",
                        title=name,
                        content=row.get("notes", ""),
                        provider="crm_csv",
                        metadata_={
                            "email": row.get("email"),
                            "organization": row.get("organization"),
                            "role": row.get("role"),
                        },
                    )
                )
                count += 1
        elif kind == "health":
            for row in reader:
                self.session.add(
                    EAHealthMetric(
                        user_id=self.user_id,
                        metric_date=row.get("date") or today,
                        metric_type=row.get("metric_type") or row.get("type", "unknown"),
                        value=float(row.get("value", 0)),
                        unit=row.get("unit"),
                    )
                )
                count += 1
        else:
            raise ValueError(f"Unknown import kind: {kind}")
        await self.session.flush()
        return {"imported": count}

    async def add_transcript(
        self,
        title: str,
        content: str,
        *,
        meeting_date: str | None = None,
        provider: str = "manual",
    ) -> EATranscript:
        actions = _extract_action_items(content)
        row = EATranscript(
            user_id=self.user_id,
            title=title,
            content=content,
            meeting_date=meeting_date,
            action_items=actions,
            provider=provider,
        )
        self.session.add(row)
        await self.session.flush()
        for action in actions:
            await self._upsert_commitment(action, provider, str(row.id))
        return row

    async def _live_stack(self) -> dict[str, Any]:
        hub = self.hub
        mock_cal = MockCalendarProvider()
        mock_email = MockEmailProvider()
        mock_tasks = MockTaskProvider()
        mock_contacts = MockContactProvider()
        mock_slack = MockSlackProvider()
        mock_docs = MockDocumentProvider()
        mock_travel = MockTravelProvider()
        mock_luxury = MockLuxuryProvider()
        mock_health = MockHealthProvider()
        mock_finance = MockFinanceProvider()

        calendar = await hub.calendar_events()
        if not calendar:
            calendar = await mock_cal.list_events(self.user_id)

        emails = await hub.recent_emails(limit=8)
        if not emails:
            emails = await mock_email.list_recent(self.user_id, limit=8)

        tasks = await hub.tasks(limit=10)
        if not tasks:
            tasks = await mock_tasks.list_tasks(self.user_id)

        contacts = await hub.contacts(limit=10)
        if not contacts:
            contacts = await mock_contacts.list_contacts(self.user_id)

        documents = await hub.documents(limit=8)
        if not documents:
            documents = await mock_docs.list_documents(self.user_id)

        slack = await hub.slack_messages(limit=6)
        if not slack:
            slack = await mock_slack.list_messages(self.user_id)

        travel = await hub.travel_confirmations()
        if not travel:
            travel = await mock_travel.list_confirmations(self.user_id)
        travel += _parse_travel_from_email(emails)

        luxury = await mock_luxury.list_items(self.user_id)
        weather = await hub.weather_snapshot()
        news = await hub.news_headlines(limit=8)
        finance = await hub.finance_lines()
        if not finance:
            finance = await mock_finance.list_lines(self.user_id)
        health = await hub.health_readings()
        if not health:
            health = await mock_health.list_readings(self.user_id)
        knowledge = await hub.knowledge_intel()

        return {
            "calendar": [_serialize_calendar(e) for e in calendar],
            "email": [_serialize_email(e) for e in emails],
            "tasks": [_serialize_task(t) for t in tasks],
            "contacts": [_serialize_contact(c) for c in contacts],
            "documents": [_serialize_document(d) for d in documents],
            "slack": [_serialize_slack(s) for s in slack],
            "travel": [_serialize_travel(t) for t in travel],
            "luxury": [_serialize_feed(i) for i in luxury],
            "weather": _serialize_weather(weather) if weather else None,
            "news": [_serialize_news(n) for n in news],
            "finance": [_serialize_finance(f) for f in finance],
            "health": [_serialize_health(h) for h in health],
            "knowledge": [_serialize_intel(k) for k in knowledge],
        }

    async def _sync_calendar(self, events: list[dict]) -> int:
        for ev in events[:20]:
            self.session.add(
                ExternalEvent(
                    user_id=self.user_id,
                    provider=ev.get("provider", "sync"),
                    title=ev.get("title", "Event"),
                    starts_at=ev.get("starts_at", ""),
                    ends_at=ev.get("ends_at"),
                    location=ev.get("location"),
                )
            )
        await self.session.flush()
        return len(events[:20])

    async def _sync_email(self, emails: list[dict]) -> int:
        for mail in emails[:15]:
            self.session.add(
                ExternalEmail(
                    user_id=self.user_id,
                    provider=mail.get("provider", "sync"),
                    sender=mail.get("sender", "?"),
                    subject=mail.get("subject", ""),
                    snippet=mail.get("snippet"),
                    received_at=mail.get("received_at", ""),
                    needs_attention=mail.get("needs_attention", False),
                )
            )
        await self.session.flush()
        return len(emails[:15])

    async def _sync_feed(self, category: str, items: list[dict]) -> int:
        now = datetime.now()
        for item in items[:20]:
            self.session.add(
                EAFeedItem(
                    user_id=self.user_id,
                    category=category,
                    title=item.get("title", category),
                    content=item.get("content") or item.get("snippet") or "",
                    provider=item.get("provider", "sync"),
                    external_id=item.get("external_id"),
                    metadata_=item.get("metadata"),
                    synced_at=now,
                )
            )
        await self.session.flush()
        return len(items[:20])

    async def _sync_finance(self, lines: list[dict]) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        for line in lines[:20]:
            self.session.add(
                EAFinanceSnapshot(
                    user_id=self.user_id,
                    snapshot_date=today,
                    label=line.get("label", "Line"),
                    amount=float(line.get("amount", 0)),
                    currency=line.get("currency", "USD"),
                    category=line.get("category"),
                )
            )
        await self.session.flush()
        return len(lines[:20])

    async def _sync_health(self, readings: list[dict]) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        for r in readings[:20]:
            self.session.add(
                EAHealthMetric(
                    user_id=self.user_id,
                    metric_date=r.get("metric_date") or today,
                    metric_type=r.get("metric_type", "unknown"),
                    value=float(r.get("value", 0)),
                    unit=r.get("unit"),
                )
            )
        await self.session.flush()
        return len(readings[:20])

    async def _extract_commitments(self, stack: dict[str, Any]) -> int:
        count = 0
        for mail in stack.get("email", []):
            if mail.get("needs_attention"):
                await self._upsert_commitment(
                    f"Follow up: {mail.get('subject', 'email')}",
                    mail.get("provider", "email"),
                    mail.get("subject"),
                    owner=mail.get("sender"),
                )
                count += 1
        for t in stack.get("tasks", []):
            if t.get("status") in ("open", "blocked"):
                await self._upsert_commitment(
                    t.get("title", "Task"),
                    t.get("provider", "task"),
                    t.get("external_id"),
                    due_at=t.get("due_at"),
                )
                count += 1
        return count

    async def _upsert_commitment(
        self,
        title: str,
        provider: str,
        source_ref: str | None,
        *,
        owner: str | None = None,
        due_at: str | None = None,
    ) -> None:
        result = await self.session.execute(
            select(EACommitment).where(
                EACommitment.user_id == self.user_id,
                EACommitment.title == title,
                EACommitment.status == "open",
            )
        )
        if result.scalar_one_or_none():
            return
        self.session.add(
            EACommitment(
                user_id=self.user_id,
                title=title,
                owner=owner,
                due_at=due_at,
                source_provider=provider,
                source_ref=source_ref,
            )
        )

    async def _load_feed_by_category(self) -> dict[str, list[dict]]:
        result = await self.session.execute(
            select(EAFeedItem)
            .where(EAFeedItem.user_id == self.user_id)
            .order_by(EAFeedItem.synced_at.desc())
            .limit(100)
        )
        grouped: dict[str, list[dict]] = {}
        for item in result.scalars().all():
            grouped.setdefault(item.category, []).append(
                {
                    "title": item.title,
                    "content": item.content,
                    "provider": item.provider,
                    "metadata": item.metadata_,
                }
            )
        return grouped

    async def _finance_summary(self) -> list[dict]:
        result = await self.session.execute(
            select(EAFinanceSnapshot)
            .where(EAFinanceSnapshot.user_id == self.user_id)
            .order_by(EAFinanceSnapshot.created_at.desc())
            .limit(10)
        )
        return [
            {
                "label": r.label,
                "amount": r.amount,
                "currency": r.currency,
                "category": r.category,
            }
            for r in result.scalars().all()
        ]

    async def _health_summary(self) -> list[dict]:
        result = await self.session.execute(
            select(EAHealthMetric)
            .where(EAHealthMetric.user_id == self.user_id)
            .order_by(EAHealthMetric.created_at.desc())
            .limit(10)
        )
        return [
            {
                "metric_type": r.metric_type,
                "value": r.value,
                "unit": r.unit,
                "metric_date": r.metric_date,
            }
            for r in result.scalars().all()
        ]

    async def _mark_integration(self, provider: str, status: str) -> None:
        result = await self.session.execute(
            select(Integration).where(
                Integration.user_id == self.user_id,
                Integration.provider == provider,
            )
        )
        row = result.scalar_one_or_none()
        if row:
            row.status = status
        else:
            self.session.add(
                Integration(user_id=self.user_id, provider=provider, status=status)
            )
        await self.session.flush()


def _tier_for_provider(provider: str) -> int:
    return {
        "google": 1,
        "microsoft": 1,
        "mock_local": 1,
        "notion": 1,
        "linear": 1,
        "slack": 1,
        "weather": 2,
        "news": 2,
        "plaid": 2,
        "crm_csv": 1,
        "finance_csv": 2,
        "health_csv": 4,
        "free_sources": 2,
        "hackernews": 1,
        "coingecko": 2,
        "gdelt": 2,
        "openalex": 5,
        "wikidata": 1,
        "nasa": 5,
        "opensky": 3,
        "restcountries": 3,
        "internet_archive": 2,
        "obsidian": 2,
        "imap": 1,
        "todoist": 1,
        "github": 1,
        "trello": 1,
        "caldav": 1,
        "fred": 2,
        "edgar": 2,
        "pubmed": 4,
        "openfda": 4,
        "cdc": 4,
    }.get(provider, 5)


def _parse_travel_from_email(emails: list[EmailMessage]) -> list[TravelConfirmation]:
    out: list[TravelConfirmation] = []
    for mail in emails:
        text = f"{mail.subject} {mail.snippet}"
        if any(p.search(text) for p in TRAVEL_PATTERNS):
            out.append(
                TravelConfirmation(
                    mail.subject[:120],
                    "email_parse",
                    mail.received_at,
                    provider=mail.provider,
                )
            )
    return out


def _extract_action_items(content: str) -> list[str]:
    lines = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith(("- [ ]", "- [x]", "ACTION:", "TODO:")):
            lines.append(s.lstrip("- [ ]xACTION:TODO:").strip())
    return lines[:10]


def _serialize_calendar(e: CalendarEvent | dict) -> dict:
    if isinstance(e, dict):
        return e
    return {
        "title": e.title,
        "starts_at": e.starts_at,
        "ends_at": e.ends_at,
        "location": e.location,
        "provider": e.provider,
    }


def _serialize_email(e: EmailMessage | dict) -> dict:
    if isinstance(e, dict):
        return e
    return {
        "sender": e.sender,
        "subject": e.subject,
        "snippet": e.snippet,
        "received_at": e.received_at,
        "needs_attention": e.needs_attention,
        "provider": e.provider,
    }


def _serialize_task(t: TaskItem | dict) -> dict:
    if isinstance(t, dict):
        return t
    return {
        "title": t.title,
        "status": t.status,
        "due_at": t.due_at,
        "project": t.project,
        "provider": t.provider,
        "external_id": t.external_id,
    }


def _serialize_contact(c: ContactRecord | dict) -> dict:
    if isinstance(c, dict):
        return c
    return {
        "title": c.name,
        "content": f"{c.role or ''} @ {c.organization or ''}".strip(),
        "email": c.email,
        "provider": c.provider,
        "metadata": {"organization": c.organization, "role": c.role},
    }


def _serialize_document(d: DocumentRef | dict) -> dict:
    if isinstance(d, dict):
        return d
    return {"title": d.title, "url": d.url, "modified_at": d.modified_at, "provider": d.provider}


def _serialize_slack(s: SlackMessage | dict) -> dict:
    if isinstance(s, dict):
        return s
    return {
        "title": f"{s.channel}: {s.author}",
        "content": s.text,
        "needs_attention": s.needs_attention,
        "provider": "slack",
    }


def _serialize_travel(t: TravelConfirmation | dict) -> dict:
    if isinstance(t, dict):
        return t
    return {
        "title": t.title,
        "content": t.confirmation_type,
        "starts_at": t.starts_at,
        "location": t.location,
        "provider": t.provider,
    }


def _serialize_feed(i: CommandFeedItem | dict) -> dict:
    if isinstance(i, dict):
        return i
    return {
        "title": i.title,
        "content": i.content,
        "provider": i.provider,
        "metadata": i.metadata,
    }


def _serialize_weather(w: WeatherSnapshot) -> dict:
    return {
        "location": w.location,
        "summary": w.summary,
        "temp_c": w.temp_c,
        "provider": w.provider,
    }


def _serialize_news(n: NewsHeadline | dict) -> dict:
    if isinstance(n, dict):
        return n
    return {"title": n.title, "source": n.source, "url": n.url, "provider": "news"}


def _serialize_finance(f: FinanceLine | dict) -> dict:
    if isinstance(f, dict):
        return f
    return {
        "label": f.label,
        "amount": f.amount,
        "currency": f.currency,
        "category": f.category,
        "provider": "finance",
    }


def _serialize_intel(k: CommandFeedItem | dict) -> dict:
    if isinstance(k, dict):
        return k
    return _serialize_feed(k)


def _serialize_health(h: HealthReading | dict) -> dict:
    if isinstance(h, dict):
        return h
    return {
        "metric_type": h.metric_type,
        "value": h.value,
        "unit": h.unit,
        "metric_date": h.metric_date,
        "provider": "health",
    }
