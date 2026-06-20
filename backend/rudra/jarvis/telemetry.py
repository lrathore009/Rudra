"""#11 — Energy/cost/latency telemetry on traces."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from rudra.autonomy.traces import Trace, log_trace
from rudra.core.config import get_settings

# Rough $/1M tokens (order-of-magnitude for HUD, not billing).
_COST_PER_1M = {
    "gpt-4o": 5.0,
    "gpt-4o-mini": 0.3,
    "gemini": 0.5,
    "claude": 3.0,
    "llama": 0.0,
    "ollama": 0.0,
}


@dataclass
class TelemetryRecord:
    provider: str = ""
    model: str = ""
    latency_ms: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    energy_wh: float = 0.0
    route: str = "local"


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    ml = model.lower()
    rate = 1.0
    for key, val in _COST_PER_1M.items():
        if key in ml:
            rate = val
            break
    total = prompt_tokens + completion_tokens
    return round((total / 1_000_000) * rate, 6)


def estimate_energy_wh(latency_ms: int, *, local: bool = True) -> float:
    """Rough edge power model: ~15W local GPU, ~0.5W cloud network."""
    hours = latency_ms / 3_600_000
    watts = 15.0 if local else 0.5
    return round(watts * hours, 6)


def log_inference_telemetry(
    *,
    model: str,
    provider: str,
    latency_ms: int,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    route: str = "local",
    summary: str = "",
) -> TelemetryRecord:
    local = route == "local" or "ollama" in model.lower()
    rec = TelemetryRecord(
        provider=provider,
        model=model,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cost_usd=estimate_cost(model, prompt_tokens, completion_tokens),
        energy_wh=estimate_energy_wh(latency_ms, local=local),
        route=route,
    )
    log_trace(
        Trace(
            kind="telemetry",
            summary=summary or f"{provider}/{model}",
            model=model,
            latency_ms=latency_ms,
            success=True,
        )
    )
    try:
        from pathlib import Path
        import json

        p = Path(get_settings().data_dir) / "telemetry.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec)) + "\n")
    except Exception:
        pass
    return rec
