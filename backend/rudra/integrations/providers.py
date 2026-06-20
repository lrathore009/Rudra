"""Calendar, email, and executive command-stack provider types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CalendarEvent:
    title: str
    starts_at: str
    ends_at: str | None = None
    location: str | None = None
    provider: str = "unknown"


@dataclass
class EmailMessage:
    sender: str
    subject: str
    snippet: str
    received_at: str
    needs_attention: bool = False
    provider: str = "unknown"


@dataclass
class TaskItem:
    title: str
    status: str = "open"
    due_at: str | None = None
    project: str | None = None
    provider: str = "unknown"
    external_id: str | None = None


@dataclass
class ContactRecord:
    name: str
    email: str | None = None
    organization: str | None = None
    role: str | None = None
    provider: str = "unknown"


@dataclass
class DocumentRef:
    title: str
    url: str | None = None
    modified_at: str | None = None
    provider: str = "unknown"


@dataclass
class SlackMessage:
    channel: str
    author: str
    text: str
    posted_at: str
    needs_attention: bool = False


@dataclass
class TravelConfirmation:
    title: str
    confirmation_type: str
    starts_at: str | None = None
    location: str | None = None
    provider: str = "email"


@dataclass
class WeatherSnapshot:
    location: str
    summary: str
    temp_c: float | None = None
    provider: str = "open_meteo"


@dataclass
class NewsHeadline:
    title: str
    source: str
    url: str | None = None


@dataclass
class FinanceLine:
    label: str
    amount: float
    currency: str = "USD"
    category: str | None = None


@dataclass
class HealthReading:
    metric_type: str
    value: float
    unit: str | None = None
    metric_date: str | None = None


@dataclass
class MeetingTranscript:
    title: str
    content: str
    meeting_date: str | None = None
    action_items: list[str] = field(default_factory=list)
    provider: str = "manual"


@dataclass
class CommandFeedItem:
    category: str
    title: str
    content: str = ""
    provider: str = "unknown"
    external_id: str | None = None
    metadata: dict | None = None


class CalendarProvider(ABC):
    @abstractmethod
    async def list_events(self, user_id: str) -> list[CalendarEvent]:
        raise NotImplementedError


class EmailProvider(ABC):
    @abstractmethod
    async def list_recent(self, user_id: str, *, limit: int = 10) -> list[EmailMessage]:
        raise NotImplementedError


class MockCalendarProvider(CalendarProvider):
    async def list_events(self, user_id: str) -> list[CalendarEvent]:
        return [
            CalendarEvent("Deep work — Rudra OS", "09:00", "11:00", "Local", "mock_local"),
            CalendarEvent("Jobsflix sync", "14:00", "14:45", "Zoom", "mock_local"),
            CalendarEvent("Founder review", "17:30", "18:00", provider="mock_local"),
            CalendarEvent("DIFC investor lunch", "12:30", "13:30", "Dubai", "mock_local"),
        ]


class MockEmailProvider(EmailProvider):
    async def list_recent(self, user_id: str, *, limit: int = 10) -> list[EmailMessage]:
        return [
            EmailMessage(
                "team@jobsflix.com",
                "Nexus AI pilot feedback",
                "Three enterprise leads asked for semantic search demo…",
                "08:12",
                needs_attention=True,
                provider="mock_local",
            ),
            EmailMessage(
                "calendar@notifications.local",
                "Tomorrow: ChemSphere milestone",
                "Reminder for architecture review.",
                "07:45",
                provider="mock_local",
            ),
            EmailMessage(
                "confirmations@emirates.com",
                "Booking confirmed: DXB → LHR 14 Jun",
                "Reference EK001. Business class.",
                "06:30",
                provider="mock_local",
            ),
        ][:limit]


class MockTaskProvider:
    async def list_tasks(self, user_id: str, *, limit: int = 10) -> list[TaskItem]:
        return [
            TaskItem("Review Rudra Jarvis deploy checklist", "open", "Today", "Rudra OS", "mock_local"),
            TaskItem("Approve Jobsflix enterprise proposal", "open", "Mon", "Jobsflix", "mock_local"),
            TaskItem("ChemSphere architecture sign-off", "blocked", "Wed", "ChemSphere", "mock_local"),
        ][:limit]


class MockContactProvider:
    async def list_contacts(self, user_id: str, *, limit: int = 10) -> list[ContactRecord]:
        return [
            ContactRecord("Sarah Chen", "sarah@venture.fund", "Horizon Capital", "Partner", "mock_local"),
            ContactRecord("Omar Al-Rashid", "omar@difc.ae", "DIFC", "Investor relations", "mock_local"),
        ][:limit]


class MockSlackProvider:
    async def list_messages(self, user_id: str, *, limit: int = 10) -> list[SlackMessage]:
        return [
            SlackMessage("#jobsflix", "Alex", "Need sign-off on pricing deck before EOD", "09:05", True),
            SlackMessage("#rudra-os", "Cursor", "Jarvis layer deployed to main", "08:40"),
        ][:limit]


class MockDocumentProvider:
    async def list_documents(self, user_id: str, *, limit: int = 10) -> list[DocumentRef]:
        return [
            DocumentRef("Board pack Q2 2026", provider="mock_local"),
            DocumentRef("ChemSphere term sheet draft", provider="mock_local"),
        ][:limit]


class MockTravelProvider:
    async def list_confirmations(self, user_id: str) -> list[TravelConfirmation]:
        return [
            TravelConfirmation("Emirates EK001 DXB→LHR", "flight", "2026-06-14 22:30", "DXB T3"),
            TravelConfirmation("Aman Tokyo — 3 nights", "hotel", "2026-06-18", "Tokyo"),
        ]


class MockLuxuryProvider:
    async def list_items(self, user_id: str) -> list[CommandFeedItem]:
        return [
            CommandFeedItem("loyalty", "Emirates Skywards Gold", "Upgrade window opens Friday", "mock_local"),
            CommandFeedItem("reservation", "Zuma Dubai — Fri 20:30", "4 guests, pending confirm", "mock_local"),
        ]


class MockHealthProvider:
    async def list_readings(self, user_id: str) -> list[HealthReading]:
        return [
            HealthReading("sleep_score", 82.0, "score", "2026-06-13"),
            HealthReading("recovery", 71.0, "percent", "2026-06-13"),
            HealthReading("hrv", 48.0, "ms", "2026-06-13"),
        ]


class MockFinanceProvider:
    async def list_lines(self, user_id: str) -> list[FinanceLine]:
        return [
            FinanceLine("Operating cash", 420000.0, "USD", "cash"),
            FinanceLine("Jobsflix MRR", 18500.0, "USD", "revenue"),
            FinanceLine("Pending invoices", -12400.0, "USD", "payables"),
        ]
