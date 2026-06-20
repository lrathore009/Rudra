"""P3 + P5 — scheduler control and trace/efficiency stats."""

from fastapi import APIRouter, Depends, HTTPException

from rudra.api.deps import require_auth
from rudra.autonomy.scheduler import Job, get_scheduler
from rudra.autonomy.traces import efficiency_stats, read_traces

router = APIRouter()


def _job_dict(j: Job) -> dict:
    return {
        "id": j.id,
        "name": j.name,
        "enabled": j.enabled,
        "interval_seconds": j.interval_seconds,
        "daily_at": j.daily_at,
        "last_run": j.last_run,
        "next_run": j.next_run,
        "last_result": j.last_result,
    }


@router.get("/scheduler/jobs")
async def list_jobs(user_id: str = Depends(require_auth)):
    return [_job_dict(j) for j in get_scheduler().jobs()]


@router.post("/scheduler/jobs/{job_id}/run")
async def run_job(job_id: str, user_id: str = Depends(require_auth)):
    sched = get_scheduler()
    if sched.get(job_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown job '{job_id}'")
    return {"job_id": job_id, "result": await sched.run_job(job_id)}


@router.post("/scheduler/jobs/{job_id}/toggle")
async def toggle_job(job_id: str, user_id: str = Depends(require_auth)):
    job = get_scheduler().get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Unknown job '{job_id}'")
    job.enabled = not job.enabled
    return {"job_id": job_id, "enabled": job.enabled}


@router.get("/traces")
async def traces(limit: int = 50, user_id: str = Depends(require_auth)):
    return read_traces(limit=limit)


@router.get("/traces/stats")
async def trace_stats(user_id: str = Depends(require_auth)):
    return efficiency_stats()
