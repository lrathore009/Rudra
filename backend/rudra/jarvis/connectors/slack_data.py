"""Slack read connector for EA inbox monitoring."""

from __future__ import annotations

from typing import Any

import httpx

from rudra.core.config import get_settings
from rudra.integrations.providers import SlackMessage
from rudra.jarvis.connectors.base import BaseConnector, ConnectorStatus


class SlackDataConnector(BaseConnector):
    name = "slack"

    def __init__(self, session):
        self.session = session

    async def connect(self, user_id: str, **credentials: Any) -> ConnectorStatus:
        token = credentials.get("bot_token") or get_settings().slack_bot_token
        if not token:
            return ConnectorStatus("slack", False, "Provide bot_token or SLACK_BOT_TOKEN")
        return ConnectorStatus("slack", True, "Slack bot token configured")

    async def status(self, user_id: str) -> ConnectorStatus:
        if get_settings().slack_bot_token:
            return ConnectorStatus("slack", True, "Slack bot token in env")
        return ConnectorStatus("slack", False, "Set SLACK_BOT_TOKEN")

    async def list_messages(self, user_id: str, *, limit: int = 10) -> list[SlackMessage]:
        token = get_settings().slack_bot_token
        if not token:
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                hist = await client.get(
                    "https://slack.com/api/conversations.history",
                    headers={"Authorization": f"Bearer {token.get_secret_value()}"},
                    params={"channel": get_settings().slack_default_channel, "limit": limit},
                )
                data = hist.json()
                if not data.get("ok"):
                    return []
                out: list[SlackMessage] = []
                for msg in data.get("messages", [])[:limit]:
                    text = msg.get("text", "")[:200]
                    out.append(
                        SlackMessage(
                            channel=get_settings().slack_default_channel,
                            author=msg.get("user", "unknown"),
                            text=text,
                            posted_at=str(msg.get("ts", "")),
                            needs_attention="?" in text or "urgent" in text.lower(),
                        )
                    )
                return out
        except Exception:
            return []
