"""Linear connector — API key based."""

from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.core.config import get_settings
from rudra.integrations.providers import TaskItem
from rudra.jarvis.connectors.base import BaseConnector, ConnectorStatus
from rudra.jarvis.models import ConnectorToken


class LinearConnector(BaseConnector):
    name = "linear"

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _api_key(self, user_id: str) -> str | None:
        result = await self.session.execute(
            select(ConnectorToken).where(
                ConnectorToken.user_id == user_id,
                ConnectorToken.provider == "linear",
            )
        )
        row = result.scalar_one_or_none()
        if row:
            return row.tokens.get("api_key") or row.tokens.get("token")
        return get_settings().linear_api_key

    async def connect(self, user_id: str, **credentials: Any) -> ConnectorStatus:
        key = credentials.get("api_key") or credentials.get("token")
        if not key:
            return ConnectorStatus("linear", False, "Provide api_key")
        result = await self.session.execute(
            select(ConnectorToken).where(
                ConnectorToken.user_id == user_id,
                ConnectorToken.provider == "linear",
            )
        )
        row = result.scalar_one_or_none()
        tokens = {"api_key": str(key)}
        if row:
            row.tokens = tokens
        else:
            self.session.add(ConnectorToken(user_id=user_id, provider="linear", tokens=tokens))
        await self.session.flush()
        return ConnectorStatus("linear", True, "Linear connected")

    async def status(self, user_id: str) -> ConnectorStatus:
        if await self._api_key(user_id):
            return ConnectorStatus("linear", True, "Linear API key on file")
        return ConnectorStatus("linear", False, "Set LINEAR_API_KEY or connect with api_key")

    async def list_tasks(self, user_id: str, *, limit: int = 10) -> list[TaskItem]:
        key = await self._api_key(user_id)
        if not key:
            return []
        query = """
        query { issues(first: 10, filter: { state: { type: { neq: \"completed\" } } }) {
          nodes { id title dueDate state { name } team { name } }
        }}
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(
                    "https://api.linear.app/graphql",
                    headers={"Authorization": key},
                    json={"query": query},
                )
                if r.status_code != 200:
                    return []
                nodes = r.json().get("data", {}).get("issues", {}).get("nodes", [])
                return [
                    TaskItem(
                        n.get("title", "Issue"),
                        n.get("state", {}).get("name", "open"),
                        n.get("dueDate"),
                        n.get("team", {}).get("name"),
                        "linear",
                        n.get("id"),
                    )
                    for n in nodes[:limit]
                ]
        except Exception:
            return []
