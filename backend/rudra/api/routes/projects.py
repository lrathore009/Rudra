"""Project OS API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.core.database import get_db
from rudra.projects.models import ProjectTask
from rudra.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    status: str = "active"
    priority: int = 3
    owner: str | None = None
    repo_url: str | None = None
    live_url: str | None = None
    local_path: str | None = None
    next_action: str | None = None
    blockers: str | None = None


class ProjectPatch(BaseModel):
    description: str | None = None
    category: str | None = None
    status: str | None = None
    priority: int | None = None
    progress_percent: float | None = None
    next_action: str | None = None
    blockers: str | None = None
    repo_url: str | None = None
    live_url: str | None = None
    local_path: str | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    category: str | None
    status: str
    priority: int
    progress_percent: float
    next_action: str | None
    blockers: str | None

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "todo"
    priority: int = 3


class TaskPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: int | None = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    status: str
    priority: int

    model_config = {"from_attributes": True}


class UpdateCreate(BaseModel):
    summary: str = Field(min_length=1)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    status: str | None = None,
    priority: int | None = None,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ProjectService(db, user_id)
    return await svc.list_projects(status=status, priority=priority)


@router.post("", response_model=ProjectResponse)
async def create_project(
    body: ProjectCreate,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ProjectService(db, user_id)
    return await svc.create_project(body.model_dump())


@router.get("/dashboard")
async def project_dashboard(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService(db, user_id).dashboard()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ProjectService(db, user_id)
    project = await svc.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def patch_project(
    project_id: uuid.UUID,
    body: ProjectPatch,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ProjectService(db, user_id)
    project = await svc.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return await svc.update_project(project, body.model_dump(exclude_unset=True))


@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    project_id: uuid.UUID,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ProjectService(db, user_id)
    if await svc.get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return await svc.list_tasks(project_id)


@router.post("/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: uuid.UUID,
    body: TaskCreate,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ProjectService(db, user_id)
    if await svc.get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return await svc.create_task(project_id, body.model_dump())


@router.patch("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def patch_task(
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    body: TaskPatch,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ProjectService(db, user_id)
    tasks = await svc.list_tasks(project_id)
    task = next((t for t in tasks if t.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return await svc.update_task(task, body.model_dump(exclude_unset=True))


@router.post("/{project_id}/updates")
async def add_update(
    project_id: uuid.UUID,
    body: UpdateCreate,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ProjectService(db, user_id)
    if await svc.get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    update = await svc.add_update(project_id, body.summary, author=user_id)
    return {"id": str(update.id), "summary": update.summary}
