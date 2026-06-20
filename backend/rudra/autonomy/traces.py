"""P5 — Trace collection + efficiency stats (foundation of the self-improvement loop).

Every autonomous run logs a compact JSONL trace (latency, steps, tools, model, success).
Aggregated stats expose efficiency (latency / step / model distribution, success rate) so
behaviour can be measured and tuned — the first rung of the improvement flywheel. Tracing
must never break a request, so all I/O is best-effort.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from rudra.core.config import get_settings


@dataclass
class Trace:
    kind: str  # "agent" | "tool" | "scheduler"
    summary: str
    model: str = ""
    latency_ms: int = 0
    steps: int = 0
    tools: list[str] = field(default_factory=list)
    success: bool = True
    ts: float = field(default_factory=time.time)


def _trace_file() -> Path:
    d = Path(get_settings().data_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d / "traces.jsonl"


def log_trace(trace: Trace) -> None:
    try:
        with _trace_file().open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(trace)) + "\n")
    except Exception:  # noqa: BLE001 - tracing is best-effort
        pass


def read_traces(limit: int = 100) -> list[dict[str, Any]]:
    p = _trace_file()
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()[-limit:]
    out: list[dict[str, Any]] = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except Exception:  # noqa: BLE001
            continue
    return out


def efficiency_stats() -> dict[str, Any]:
    traces = read_traces(limit=1000)
    if not traces:
        return {"count": 0}
    lat = [int(t.get("latency_ms", 0)) for t in traces]
    by_model: dict[str, int] = {}
    tool_counts: dict[str, int] = {}
    for t in traces:
        model = t.get("model") or "?"
        by_model[model] = by_model.get(model, 0) + 1
        for tool in t.get("tools", []):
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
    successes = sum(1 for t in traces if t.get("success"))
    lat_sorted = sorted(lat)
    return {
        "count": len(traces),
        "success_rate": round(successes / len(traces), 3),
        "avg_latency_ms": int(sum(lat) / len(lat)),
        "p95_latency_ms": lat_sorted[min(len(lat_sorted) - 1, int(len(lat_sorted) * 0.95))],
        "avg_steps": round(sum(int(t.get("steps", 0)) for t in traces) / len(traces), 2),
        "by_model": by_model,
        "top_tools": dict(sorted(tool_counts.items(), key=lambda x: -x[1])[:10]),
    }
