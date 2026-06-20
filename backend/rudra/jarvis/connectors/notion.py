"""Notion connector — API token based."""

from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.core.config import get_settings
from rudra.integrations.providers import DocumentRef, TaskItem
from rudra.jarvis.connectors.base import BaseConnector, ConnectorStatus
from rudra.jarvis.models import ConnectorToken


class NotionConnector(BaseConnector):
    name = "notion"

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _token(self, user_id: str) -> str | None:
        row = await self._row(user_id)
        if row:
            return row.tokens.get("api_token") or row.tokens.get("token")
        return get_settings().notion_api_token

    async def _row(self, user_id: str):
        result = await self.session.execute(
            select(ConnectorToken).where(
                ConnectorToken.user_id == user_id,
                ConnectorToken.provider == "notion",
            )
        )
        return result.scalar_one_or_none()

    async def connect(self, user_id: str, **credentials: Any) -> ConnectorStatus:
        token = credentials.get("api_token") or credentials.get("token")
        if not token:
            return ConnectorStatus("notion", False, "Provide api_token")
        existing = await self._row(user_id)
        tokens = {"api_token": str(token)}
        if existing:
            existing.tokens = tokens
        else:
            self.session.add(ConnectorToken(user_id=user_id, provider="notion", tokens=tokens))
        await self.session.flush()
        return ConnectorStatus("notion", True, "Notion connected")

    async def status(self, user_id: str) -> ConnectorStatus:
        if await self._token(user_id):
            return ConnectorStatus("notion", True, "Notion API token on file")
        return ConnectorStatus("notion", False, "Set NOTION_API_TOKEN or POST connect with api_token")

    async def list_tasks(self, user_id: str, *, limit: int = 10) -> list[TaskItem]:
        token = await self._token(user_id)
        if not token:
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(
                    "https://api.notion.com/v1/search",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Notion-Version": "2022-06-28",
                    },
                    json={"page_size": limit, "filter": {"property": "object", "value": "page"}},
                )
                if r.status_code != 200:
                    return []
                out: list[TaskItem] = []
                for item in r.json().get("results", [])[:limit]:
                    title = _notion_title(item)
                    out.append(TaskItem(title, "open", provider="notion", external_id=item.get("id")))
                return out
        except Exception:
            return []

    async def list_documents(self, user_id: str, *, limit: int = 10) -> list[DocumentRef]:
        tasks = await self.list_tasks(user_id, limit=limit)
        return [
            DocumentRef(t.title, url=t.external_id, provider="notion")
            for t in tasks
        ]


def _notion_title(item: dict) -> str:
    props = item.get("properties", {})
    for val in props.values():
        if val.get("type") == "title":
            parts = val.get("title", [])
            if parts:
                return parts[0].get("plain_text", "Notion page")
    return item.get("url", "Notion page")[:80]
