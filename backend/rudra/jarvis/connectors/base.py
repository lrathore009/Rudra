"""#2 — Connector framework for real life-data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from rudra.integrations.providers import CalendarEvent, EmailMessage


@dataclass
class ConnectorStatus:
    provider: str
    connected: bool
    detail: str = ""


class BaseConnector(ABC):
    name: str

    @abstractmethod
    async def connect(self, user_id: str, **credentials: Any) -> ConnectorStatus:
        ...

    @abstractmethod
    async def status(self, user_id: str) -> ConnectorStatus:
        ...

    async def calendar_events(self, user_id: str) -> list[CalendarEvent]:
        return []

    async def recent_emails(self, user_id: str, *, limit: int = 10) -> list[EmailMessage]:
        return []
