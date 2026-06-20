"""#6 — Slack channel adapter for Jarvis in your pocket."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

from rudra.core.config import get_settings
from rudra.core.logging import get_logger
from rudra.jarvis.events import EventType, get_event_bus

logger = get_logger(__name__)


def verify_slack_signature(body: bytes, timestamp: str, signature: str) -> bool:
    secret = get_settings().slack_signing_secret
    if not secret:
        return False
    if abs(time.time() - int(timestamp)) > 300:
        return False
    base = f"v0:{timestamp}:{body.decode('utf-8')}"
    digest = hmac.new(secret.get_secret_value().encode(), base.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"v0={digest}", signature)


async def handle_slack_event(payload: dict) -> dict:
    """Process Slack event_callback and return response text."""
    get_event_bus().publish(EventType.CHANNEL_MESSAGE, {"channel": "slack", "type": payload.get("type")})
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}
    event = payload.get("event", {})
    text = str(event.get("text", "")).strip()
    if not text or event.get("bot_id"):
        return {"ok": True, "skipped": True}
    from rudra.agents.base import AgentContext, AgentOrchestrator, AgentType
    from rudra.jarvis.learning import suggest_agent_for_query

    orch = AgentOrchestrator()
    ctx = AgentContext(user_id="owner", session_id=f"slack-{event.get('channel', 'dm')}")
    suggested = suggest_agent_for_query(text)
    if suggested:
        result = await orch.invoke(AgentType(suggested), text, ctx)
    else:
        result = await orch.route(text, ctx)
    return {"ok": True, "response": result.content[:3000], "agent": result.agent_type.value}
