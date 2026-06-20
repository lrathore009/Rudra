"""P3 — In-process async scheduler for scheduled + continuous autonomous agents.

Dependency-free (no Celery/Redis broker): a single asyncio loop wakes each tick and fires
due jobs. Ships a daily ``morning_digest`` job and supports recurring interval "monitor"
jobs. This is the right shape for a single-owner local app; swap in Celery for multi-node.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Awaitable, Callable

from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)

JobFn = Callable[[], Awaitable[str]]


@dataclass
class Job:
    id: str
    name: str
    fn: JobFn
    interval_seconds: int | None = None  # recurring monitors
    daily_at: str | None = None  # "HH:MM" local for daily jobs
    enabled: bool = True
    last_run: float | None = None
    last_result: str | None = None
    next_run: float | None = None

    def compute_next(self, now: float) -> float:
        if self.interval_seconds:
            return now + self.interval_seconds
        if self.daily_at:
            hh, mm = (int(x) for x in self.daily_at.split(":"))
            dt = datetime.fromtimestamp(now).replace(hour=hh, minute=mm, second=0, microsecond=0)
            ts = dt.timestamp()
            return ts if ts > now else ts + 86400
        return now + 3600


class Scheduler:
    def __init__(self, tick_seconds: int = 30) -> None:
        self.tick = tick_seconds
        self._jobs: dict[str, Job] = {}
        self._task: asyncio.Task | None = None
        self._running = False

    def add_job(self, job: Job) -> None:
        job.next_run = job.compute_next(time.time())
        self._jobs[job.id] = job

    def jobs(self) -> list[Job]:
        return list(self._jobs.values())

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    async def run_job(self, job_id: str) -> str:
        job = self._jobs.get(job_id)
        if not job:
            return f"Unknown job '{job_id}'"
        return await self._fire(job)

    async def _fire(self, job: Job) -> str:
        from rudra.autonomy.traces import Trace, log_trace

        started = time.time()
        try:
            result = await job.fn()
            ok = True
        except Exception as e:  # noqa: BLE001
            result = f"error: {e}"
            ok = False
            logger.warning("job_failed", job=job.id, error=str(e)[:160])
        job.last_run = time.time()
        job.last_result = (result or "")[:500]
        job.next_run = job.compute_next(job.last_run)
        log_trace(
            Trace(
                kind="scheduler",
                summary=f"{job.id}: {(result or '')[:80]}",
                latency_ms=int((time.time() - started) * 1000),
                success=ok,
            )
        )
        return result

    async def _loop(self) -> None:
        self._running = True
        while self._running:
            now = time.time()
            for job in list(self._jobs.values()):
                if job.enabled and job.next_run and now >= job.next_run:
                    await self._fire(job)
            await asyncio.sleep(self.tick)

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())
            logger.info("scheduler_started", jobs=len(self._jobs))

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except BaseException:  # noqa: BLE001 - cancellation is expected
                pass
            self._task = None


_scheduler: Scheduler | None = None


def get_scheduler() -> Scheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
        _register_default_jobs(_scheduler)
    return _scheduler


def _register_default_jobs(sched: Scheduler) -> None:
    sched.add_job(
        Job(
            id="morning_digest",
            name="Morning Digest",
            fn=morning_digest,
            daily_at=get_settings().morning_digest_time,
        )
    )


async def morning_digest() -> str:
    """Scheduled daily briefing stored as memory."""
    from rudra.core.database import get_session_factory
    from rudra.integrations.service import BriefingService
    from rudra.memory.models.memory import MemoryType
    from rudra.memory.service import MemoryService

    factory = get_session_factory()
    async with factory() as db:
        briefing = await BriefingService(db, "owner").generate_daily()
        svc = MemoryService(db, "owner")
        await svc.create(
            MemoryType.EPISODIC,
            title=f"Morning Digest {briefing.briefing_date}",
            content=briefing.content,
            importance=0.8,
            source="scheduler:morning_digest",
            tags=["digest", "scheduled", "briefing"],
        )
        await db.commit()
    return briefing.content[:500]
