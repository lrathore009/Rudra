"""#4 — Trace-driven learning hints for agent routing."""

from __future__ import annotations

from collections import Counter
from typing import Any

from rudra.agents.types import AgentType
from rudra.autonomy.traces import read_traces


def routing_hints_from_traces(limit: int = 500) -> dict[str, Any]:
    traces = read_traces(limit=limit)
    agent_counts: Counter[str] = Counter()
    tool_counts: Counter[str] = Counter()
    failures = 0
    for t in traces:
        if not t.get("success", True):
            failures += 1
        summary = str(t.get("summary", "")).lower()
        for agent in AgentType:
            if agent.value in summary:
                agent_counts[agent.value] += 1
        for tool in t.get("tools", []):
            tool_counts[str(tool)] += 1
    return {
        "trace_count": len(traces),
        "failure_rate": round(failures / max(len(traces), 1), 3),
        "top_agents": dict(agent_counts.most_common(5)),
        "top_tools": dict(tool_counts.most_common(10)),
    }


def suggest_agent_for_query(query: str, hints: dict[str, Any] | None = None) -> str | None:
    """Lightweight trace-informed boost — returns agent type or None."""
    hints = hints or routing_hints_from_traces()
    q = query.lower()
    keyword_map = {
        "research": AgentType.RESEARCH_ANALYST.value,
        "travel": AgentType.TRAVEL.value,
        "write": AgentType.WRITING.value,
        "presentation": AgentType.PRESENTATION.value,
        "luxury": AgentType.LUXURY_ANALYST.value,
        "concierge": AgentType.CONCIERGE.value,
        "calendar": AgentType.EXECUTIVE_ASSISTANT.value,
        "briefing": AgentType.EXECUTIVE_ASSISTANT.value,
        "vendor": AgentType.OPERATIONS.value,
    }
    for kw, agent in keyword_map.items():
        if kw in q:
            return agent
    top = hints.get("top_agents", {})
    if top:
        return next(iter(top.keys()))
    return None
