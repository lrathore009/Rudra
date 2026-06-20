"""P5 — trace logging + efficiency stats tests (isolated temp store)."""

from rudra.autonomy import traces


def test_log_read_and_stats(tmp_path, monkeypatch):
    tf = tmp_path / "traces.jsonl"
    monkeypatch.setattr(traces, "_trace_file", lambda: tf)

    traces.log_trace(
        traces.Trace(kind="agent", summary="t1", model="m", latency_ms=100, steps=2,
                     tools=["calculator"], success=True)
    )
    traces.log_trace(
        traces.Trace(kind="agent", summary="t2", model="m", latency_ms=300, steps=1,
                     tools=["web_search"], success=False)
    )

    rows = traces.read_traces()
    assert len(rows) == 2

    stats = traces.efficiency_stats()
    assert stats["count"] == 2
    assert stats["by_model"]["m"] == 2
    assert stats["success_rate"] == 0.5
    assert stats["avg_latency_ms"] == 200
    assert "calculator" in stats["top_tools"]


def test_empty_stats(tmp_path, monkeypatch):
    monkeypatch.setattr(traces, "_trace_file", lambda: tmp_path / "none.jsonl")
    assert traces.efficiency_stats() == {"count": 0}
    assert traces.read_traces() == []
