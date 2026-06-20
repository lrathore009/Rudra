"""Project OS service — CRUD, tasks, dashboard."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.projects.intelligence import ProjectIntelligenceService
from rudra.projects.models import FounderProject, ProjectStatus, ProjectTask, ProjectUpdate
from rudra.projects.seed import SEED_PROJECTS


class ProjectService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.intelligence = ProjectIntelligenceService(session, user_id)

    async def list_projects(
        self,
        *,
        status: str | None = None,
        priority: int | None = None,
        limit: int = 50,
    ) -> list[FounderProject]:
        stmt = (
            select(FounderProject)
            .where(FounderProject.user_id == self.user_id)
            .order_by(FounderProject.priority, FounderProject.name)
            .limit(limit)
        )
        if status:
            stmt = stmt.where(FounderProject.status == status)
        if priority is not None:
            stmt = stmt.where(FounderProject.priority <= priority)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_project(self, project_id: uuid.UUID) -> FounderProject | None:
        result = await self.session.execute(
            select(FounderProject).where(
                FounderProject.id == project_id,
                FounderProject.user_id == self.user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> FounderProject | None:
        result = await self.session.execute(
            select(FounderProject).where(
                FounderProject.user_id == self.user_id,
                func.lower(FounderProject.name) == name.lower(),
            )
        )
        return result.scalar_one_or_none()

    async def create_project(self, data: dict[str, Any]) -> FounderProject:
        project = FounderProject(user_id=self.user_id, **data)
        self.session.add(project)
        await self.session.flush()
        return project

    async def update_project(self, project: FounderProject, data: dict[str, Any]) -> FounderProject:
        for key, value in data.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)
        await self.session.flush()
        return project

    async def list_tasks(self, project_id: uuid.UUID) -> list[ProjectTask]:
        result = await self.session.execute(
            select(ProjectTask).where(ProjectTask.project_id == project_id).order_by(ProjectTask.priority)
        )
        return list(result.scalars().all())

    async def create_task(self, project_id: uuid.UUID, data: dict[str, Any]) -> ProjectTask:
        task = ProjectTask(project_id=project_id, **data)
        self.session.add(task)
        await self.session.flush()
        project = await self.get_project(project_id)
        if project:
            project.progress_percent = await self.intelligence.calculate_progress(project)
        return task

    async def update_task(self, task: ProjectTask, data: dict[str, Any]) -> ProjectTask:
        for key, value in data.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        await self.session.flush()
        project = await self.get_project(task.project_id)
        if project:
            project.progress_percent = await self.intelligence.calculate_progress(project)
        return task

    async def add_update(self, project_id: uuid.UUID, summary: str, author: str | None = None) -> ProjectUpdate:
        update = ProjectUpdate(project_id=project_id, summary=summary, author=author)
        self.session.add(update)
        await self.session.flush()
        return update

    async def dashboard(self) -> dict[str, Any]:
        projects = await self.list_projects(limit=100)
        stale = await self.intelligence.identify_stale()
        blocked = await self.intelligence.identify_blocked()
        cards = []
        for p in projects:
            progress = await self.intelligence.calculate_progress(p)
            cards.append(
                {
                    "id": str(p.id),
                    "name": p.name,
                    "status": p.status,
                    "priority": p.priority,
                    "progress_percent": progress,
                    "next_action": await self.intelligence.recommend_next_action(p),
                    "blockers": p.blockers,
                    "category": p.category,
                }
            )
        return {
            "projects": cards,
            "stale_count": len(stale),
            "blocked_count": len(blocked),
            "weekly_briefing": await self.intelligence.weekly_briefing(projects),
        }

    async def find_project_in_text(self, text: str) -> FounderProject | None:
        lower = text.lower()
        projects = await self.list_projects(limit=100)
        matches = [p for p in projects if p.name.lower() in lower]
        if not matches:
            return None
        return sorted(matches, key=lambda p: len(p.name), reverse=True)[0]

    async def context_for_agent(self, project: FounderProject) -> dict[str, Any]:
        tasks = await self.list_tasks(project.id)
        return {
            "project": {
                "name": project.name,
                "status": project.status,
                "priority": project.priority,
                "progress_percent": await self.intelligence.calculate_progress(project),
                "next_action": await self.intelligence.recommend_next_action(project),
                "blockers": project.blockers,
                "description": project.description,
            },
            "open_tasks": [
                {"title": t.title, "status": t.status, "priority": t.priority}
                for t in tasks
                if t.status != "done"
            ][:10],
        }

    async def seed_projects(self) -> int:
        count = 0
        for item in SEED_PROJECTS:
            if await self.get_by_name(item["name"]):
                continue
            await self.create_project({**item, "owner": self.user_id})
            count += 1
        return count
