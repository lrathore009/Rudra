"""Connector registry — all Phase 1 EA tiers and connect order."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from rudra.integrations.providers import (
    CalendarEvent,
    CommandFeedItem,
    ContactRecord,
    DocumentRef,
    EmailMessage,
    FinanceLine,
    HealthReading,
    MockCalendarProvider,
    MockContactProvider,
    MockDocumentProvider,
    MockEmailProvider,
    MockFinanceProvider,
    MockHealthProvider,
    MockSlackProvider,
    MockTaskProvider,
    MockTravelProvider,
    NewsHeadline,
    SlackMessage,
    TaskItem,
    TravelConfirmation,
    WeatherSnapshot,
)
from rudra.jarvis.connectors.base import ConnectorStatus
from rudra.jarvis.connectors.google import GoogleConnector
from rudra.jarvis.connectors.linear import LinearConnector
from rudra.jarvis.connectors.microsoft import MicrosoftConnector
from rudra.jarvis.connectors.news import NewsConnector
from rudra.jarvis.connectors.notion import NotionConnector
from rudra.jarvis.connectors.slack_data import SlackDataConnector
from rudra.jarvis.connectors.weather import WeatherConnector
from rudra.jarvis.connectors.free_sources import FreeSourcesHub

# Connect order: Google → Notion → Linear → Slack → weather/news → Microsoft → mock
ALL_PROVIDERS = (
    "google",
    "notion",
    "linear",
    "slack",
    "weather",
    "news",
    "microsoft",
    "mock_local",
)


class ConnectorHub:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.google = GoogleConnector(session)
        self.notion = NotionConnector(session)
        self.linear = LinearConnector(session)
        self.slack = SlackDataConnector(session)
        self.weather = WeatherConnector(session)
        self.news = NewsConnector(session)
        self.microsoft = MicrosoftConnector(session)
        self._mock_cal = MockCalendarProvider()
        self._mock_email = MockEmailProvider()
        self._mock_tasks = MockTaskProvider()
        self._mock_contacts = MockContactProvider()
        self._mock_slack = MockSlackProvider()
        self._mock_docs = MockDocumentProvider()
        self._mock_travel = MockTravelProvider()
        self._mock_finance = MockFinanceProvider()
        self._mock_health = MockHealthProvider()
        self.free = FreeSourcesHub()

    async def list_status(self) -> list[ConnectorStatus]:
        statuses = [
            await self.google.status(self.user_id),
            await self.notion.status(self.user_id),
            await self.linear.status(self.user_id),
            await self.slack.status(self.user_id),
            await self.weather.status(self.user_id),
            await self.news.status(self.user_id),
            await self.microsoft.status(self.user_id),
            ConnectorStatus("mock_local", True, "Built-in demo stack (all tiers)"),
        ]
        if self.free.enabled:
            free_rows = await self.free.list_status()
            free_count = sum(1 for s in free_rows if s.get("connected"))
            statuses.append(
                ConnectorStatus(
                    "free_sources",
                    True,
                    f"{free_count} free intel sources active",
                )
            )
        return statuses

    async def connect(self, provider: str, **credentials) -> ConnectorStatus:
        mapping = {
            "google": self.google.connect,
            "notion": self.notion.connect,
            "linear": self.linear.connect,
            "slack": self.slack.connect,
            "weather": self.weather.connect,
            "news": self.news.connect,
            "microsoft": self.microsoft.connect,
            "mock_local": self._connect_mock,
        }
        handler = mapping.get(provider)
        if not handler:
            return ConnectorStatus(provider, False, f"Unknown provider '{provider}'")
        return await handler(self.user_id, **credentials)

    async def _connect_mock(self, user_id: str, **_) -> ConnectorStatus:
        return ConnectorStatus("mock_local", True, "Mock executive stack enabled")

    async def calendar_events(self) -> list[CalendarEvent]:
        events: list[CalendarEvent] = []
        for source in (self.google, self.microsoft):
            events.extend(await source.calendar_events(self.user_id))
        events.extend(await self.free.calendar_events())
        if events:
            return events
        return await self._mock_cal.list_events(self.user_id)

    async def recent_emails(self, *, limit: int = 10) -> list[EmailMessage]:
        emails: list[EmailMessage] = []
        for source in (self.google, self.microsoft):
            emails.extend(await source.recent_emails(self.user_id, limit=limit))
        emails.extend(await self.free.recent_emails(limit=limit))
        if emails:
            return emails[:limit]
        return await self._mock_email.list_recent(self.user_id, limit=limit)

    async def tasks(self, *, limit: int = 10) -> list[TaskItem]:
        items: list[TaskItem] = []
        items.extend(await self.notion.list_tasks(self.user_id, limit=limit))
        items.extend(await self.linear.list_tasks(self.user_id, limit=limit))
        items.extend(await self.free.tasks(limit=limit))
        if items:
            return items[:limit]
        return await self._mock_tasks.list_tasks(self.user_id, limit=limit)

    async def contacts(self, *, limit: int = 10) -> list[ContactRecord]:
        free = await self.free.contacts(limit=limit)
        if free:
            return free
        return await self._mock_contacts.list_contacts(self.user_id, limit=limit)

    async def documents(self, *, limit: int = 10) -> list[DocumentRef]:
        docs: list[DocumentRef] = []
        docs.extend(await self.notion.list_documents(self.user_id, limit=limit))
        drive = await self.google.list_drive_files(self.user_id, limit=limit)
        if drive:
            docs.extend(
                DocumentRef(
                    f.get("name", "File"),
                    url=f.get("id"),
                    modified_at=f.get("modifiedTime"),
                    provider="google",
                )
                for f in drive
            )
        docs.extend(await self.free.documents(limit=limit))
        if docs:
            return docs[:limit]
        return await self._mock_docs.list_documents(self.user_id, limit=limit)

    async def slack_messages(self, *, limit: int = 10) -> list[SlackMessage]:
        msgs = await self.slack.list_messages(self.user_id, limit=limit)
        if msgs:
            return msgs
        return await self._mock_slack.list_messages(self.user_id, limit=limit)

    async def travel_confirmations(self) -> list[TravelConfirmation]:
        travel = await self.free.travel_confirmations()
        if travel:
            return travel
        return await self._mock_travel.list_confirmations(self.user_id)

    async def weather_snapshot(self) -> WeatherSnapshot | None:
        return await self.weather.snapshot(self.user_id)

    async def news_headlines(self, *, limit: int = 5) -> list[NewsHeadline]:
        headlines = await self.news.headlines(self.user_id, limit=limit)
        extra = await self.free.news_headlines(limit=limit)
        merged = headlines + extra
        seen: set[str] = set()
        out: list[NewsHeadline] = []
        for h in merged:
            key = h.title[:80]
            if key in seen:
                continue
            seen.add(key)
            out.append(h)
            if len(out) >= limit:
                break
        return out

    async def finance_lines(self) -> list[FinanceLine]:
        lines = await self.free.finance_lines()
        if lines:
            return lines
        return await self._mock_finance.list_lines(self.user_id)

    async def health_readings(self) -> list[HealthReading]:
        readings = await self.free.health_readings()
        if readings:
            return readings
        return await self._mock_health.list_readings(self.user_id)

    async def knowledge_intel(self) -> list[CommandFeedItem]:
        return await self.free.knowledge_intel()
