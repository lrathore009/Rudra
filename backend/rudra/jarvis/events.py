"""#17 — EventBus: connective tissue for proactive Jarvis behavior."""

from __future__ import annotations

import threading
from collections import defaultdict
from enum import Enum
from typing import Any, Callable

from rudra.core.logging import get_logger

logger = get_logger(__name__)


class EventType(str, Enum):
    INFERENCE_START = "inference_start"
    INFERENCE_END = "inference_end"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_END = "tool_call_end"
    MEMORY_RETRIEVE = "memory_retrieve"
    AGENT_TURN_END = "agent_turn_end"
    BRIEFING_GENERATED = "briefing_generated"
    OPERATOR_TICK = "operator_tick"
    CHANNEL_MESSAGE = "channel_message"
    SECURITY_SCAN = "security_scan"
    SYNC_COMPLETE = "sync_complete"
    RESEARCH_STARTED = "research_started"
    RESEARCH_COMPLETED = "research_completed"


Handler = Callable[[EventType, dict[str, Any]], None]


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[EventType, list[Handler]] = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        with self._lock:
            self._subs[event_type].append(handler)

    def publish(self, event_type: EventType, payload: dict[str, Any] | None = None) -> None:
        payload = payload or {}
        for handler in list(self._subs.get(event_type, [])):
            try:
                handler(event_type, payload)
            except Exception as e:  # noqa: BLE001
                logger.warning("event_handler_failed", event=event_type.value, error=str(e)[:120])


_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus
