"""P3 — in-process scheduler tests (no broker, no LLM)."""

import time

from rudra.autonomy.scheduler import Job, Scheduler


async def test_run_job_invokes_fn(monkeypatch):
    # Avoid touching the real trace file.
    monkeypatch.setattr("rudra.autonomy.traces.log_trace", lambda *_a, **_k: None)

    calls = {"n": 0}

    async def job_fn():
        calls["n"] += 1
        return "did work"

    sched = Scheduler(tick_seconds=1)
    sched.add_job(Job(id="t", name="Test", fn=job_fn, interval_seconds=3600))

    result = await sched.run_job("t")

    assert result == "did work"
    assert calls["n"] == 1
    job = sched.get("t")
    assert job is not None
    assert job.last_run is not None
    assert job.last_result == "did work"
    assert job.next_run and job.next_run > time.time()


async def test_run_unknown_job():
    sched = Scheduler()
    assert "Unknown job" in await sched.run_job("nope")


async def test_failing_job_is_caught(monkeypatch):
    monkeypatch.setattr("rudra.autonomy.traces.log_trace", lambda *_a, **_k: None)

    async def boom():
        raise ValueError("kaboom")

    sched = Scheduler()
    sched.add_job(Job(id="b", name="Boom", fn=boom, interval_seconds=60))
    result = await sched.run_job("b")
    assert "error" in result.lower()


def test_default_scheduler_has_morning_digest():
    from rudra.autonomy.scheduler import get_scheduler

    ids = {j.id for j in get_scheduler().jobs()}
    assert "morning_digest" in ids
