"""Google OAuth connector — Gmail + Calendar when credentials configured."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.core.config import get_settings
from rudra.integrations.providers import CalendarEvent, EmailMessage
from rudra.jarvis.connectors.base import BaseConnector, ConnectorStatus
from rudra.jarvis.models import ConnectorToken


class GoogleConnector(BaseConnector):
    name = "google"

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _tokens(self, user_id: str) -> dict[str, Any] | None:
        result = await self.session.execute(
            select(ConnectorToken).where(
                ConnectorToken.user_id == user_id,
                ConnectorToken.provider == "google",
            )
        )
        row = result.scalar_one_or_none()
        return row.tokens if row else None

    async def connect(self, user_id: str, **credentials: Any) -> ConnectorStatus:
        settings = get_settings()
        if not settings.google_client_id or not settings.google_client_secret:
            return ConnectorStatus(
                "google",
                False,
                "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env, then POST /jarvis/connect/google",
            )
        refresh = credentials.get("refresh_token") or credentials.get("token_json")
        if not refresh:
            return ConnectorStatus("google", False, "Provide refresh_token or token_json")
        tokens = refresh if isinstance(refresh, dict) else {"refresh_token": str(refresh)}
        result = await self.session.execute(
            select(ConnectorToken).where(
                ConnectorToken.user_id == user_id,
                ConnectorToken.provider == "google",
            )
        )
        row = result.scalar_one_or_none()
        if row:
            row.tokens = tokens
        else:
            self.session.add(
                ConnectorToken(user_id=user_id, provider="google", tokens=tokens)
            )
        await self.session.flush()
        return ConnectorStatus("google", True, "Google tokens stored")

    async def status(self, user_id: str) -> ConnectorStatus:
        tokens = await self._tokens(user_id)
        if tokens:
            return ConnectorStatus("google", True, "OAuth tokens on file")
        if get_settings().google_client_id:
            return ConnectorStatus("google", False, "OAuth configured — connect to authorize")
        return ConnectorStatus("google", False, "Not configured")

    async def calendar_events(self, user_id: str) -> list[CalendarEvent]:
        tokens = await self._tokens(user_id)
        if not tokens:
            return []
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_info(tokens)
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            events_result = service.events().list(calendarId="primary", maxResults=10, singleEvents=True).execute()
            out: list[CalendarEvent] = []
            for item in events_result.get("items", []):
                start = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date", "")
                out.append(
                    CalendarEvent(
                        title=item.get("summary", "Event"),
                        starts_at=start,
                        location=item.get("location"),
                    )
                )
            return out
        except Exception:
            return []

    async def recent_emails(self, user_id: str, *, limit: int = 10) -> list[EmailMessage]:
        tokens = await self._tokens(user_id)
        if not tokens:
            return []
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_info(tokens)
            service = build("gmail", "v1", credentials=creds, cache_discovery=False)
            resp = service.users().messages().list(userId="me", maxResults=limit, q="is:unread").execute()
            out: list[EmailMessage] = []
            for mid in resp.get("messages", [])[:limit]:
                msg = service.users().messages().get(userId="me", id=mid["id"], format="metadata").execute()
                headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
                out.append(
                    EmailMessage(
                        sender=headers.get("From", "?"),
                        subject=headers.get("Subject", "(no subject)"),
                        snippet=msg.get("snippet", "")[:200],
                        received_at=headers.get("Date", ""),
                        needs_attention=True,
                    )
                )
            return out
        except Exception:
            return []

    async def list_drive_files(self, user_id: str, *, limit: int = 10) -> list[dict]:
        tokens = await self._tokens(user_id)
        if not tokens:
            return []
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_info(tokens)
            service = build("drive", "v3", credentials=creds, cache_discovery=False)
            resp = service.files().list(pageSize=limit, fields="files(id,name,modifiedTime)").execute()
            return resp.get("files", [])
        except Exception:
            return []
