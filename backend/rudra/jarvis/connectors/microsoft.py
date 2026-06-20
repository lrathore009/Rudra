"""Microsoft 365 connector scaffold — Graph API when token provided."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.integrations.providers import CalendarEvent, EmailMessage
from rudra.jarvis.connectors.base import BaseConnector, ConnectorStatus
from rudra.jarvis.models import ConnectorToken


class MicrosoftConnector(BaseConnector):
    name = "microsoft"

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _tokens(self, user_id: str) -> dict | None:
        result = await self.session.execute(
            select(ConnectorToken).where(
                ConnectorToken.user_id == user_id,
                ConnectorToken.provider == "microsoft",
            )
        )
        row = result.scalar_one_or_none()
        return row.tokens if row else None

    async def connect(self, user_id: str, **credentials: Any) -> ConnectorStatus:
        token_json = credentials.get("token_json") or credentials.get("access_token")
        if not token_json:
            return ConnectorStatus("microsoft", False, "Provide token_json from Microsoft OAuth")
        tokens = token_json if isinstance(token_json, dict) else {"access_token": str(token_json)}
        result = await self.session.execute(
            select(ConnectorToken).where(
                ConnectorToken.user_id == user_id,
                ConnectorToken.provider == "microsoft",
            )
        )
        row = result.scalar_one_or_none()
        if row:
            row.tokens = tokens
        else:
            self.session.add(
                ConnectorToken(user_id=user_id, provider="microsoft", tokens=tokens)
            )
        await self.session.flush()
        return ConnectorStatus("microsoft", True, "Microsoft tokens stored")

    async def status(self, user_id: str) -> ConnectorStatus:
        if await self._tokens(user_id):
            return ConnectorStatus("microsoft", True, "Microsoft Graph tokens on file")
        return ConnectorStatus("microsoft", False, "Connect with Microsoft OAuth token_json")

    async def calendar_events(self, user_id: str) -> list[CalendarEvent]:
        # Graph API integration point — returns empty until token + HTTP wired
        return []

    async def recent_emails(self, user_id: str, *, limit: int = 10) -> list[EmailMessage]:
        return []
