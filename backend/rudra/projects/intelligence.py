"""Project intelligence — progress, stale detection, briefings."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.projects.models import FounderProject, ProjectStatus, ProjectTask


class ProjectIntelligenceService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def calculate_progress(self, project: FounderProject) -> float:
        result = await self.session.execute(
            select(func.count(ProjectTask.id)).where(ProjectTask.project_id == project.id)
        )
        total = result.scalar_one() or 0
        if total == 0:
            return project.progress_percent
        done = await self.session.execute(
            select(func.count(ProjectTask.id)).where(
                ProjectTask.project_id == project.id,
                ProjectTask.status == "done",
            )
        )
        completed = done.scalar_one() or 0
        return round((completed / total) * 100.0, 1)

    async def identify_stale(self, *, days: int = 14) -> list[FounderProject]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        result = await self.session.execute(
            select(FounderProject).where(
                FounderProject.user_id == self.user_id,
                FounderProject.status == ProjectStatus.ACTIVE.value,
                FounderProject.updated_at < cutoff,
            )
        )
        return list(result.scalars().all())

    async def identify_blocked(self) -> list[FounderProject]:
        result = await self.session.execute(
            select(FounderProject).where(
                FounderProject.user_id == self.user_id,
                FounderProject.status.in_([ProjectStatus.BLOCKED.value, ProjectStatus.ACTIVE.value]),
            )
        )
        projects = list(result.scalars().all())
        return [p for p in projects if p.blockers or p.status == ProjectStatus.BLOCKED.value]

    async def recommend_next_action(self, project: FounderProject) -> str:
        if project.next_action:
            return project.next_action
        if project.blockers:
            return f"Resolve blocker: {project.blockers[:120]}"
        progress = await self.calculate_progress(project)
        if progress < 30:
            return f"Define milestones and first shippable slice for {project.name}."
        return f"Review open tasks and update progress for {project.name}."

    async def weekly_briefing(self, projects: list[FounderProject]) -> str:
        stale = await self.identify_stale()
        blocked = await self.identify_blocked()
        lines = ["# Founder Weekly Briefing", ""]
        lines.append("## Priority projects")
        for p in sorted(projects, key=lambda x: x.priority)[:5]:
            progress = await self.calculate_progress(p)
            action = await self.recommend_next_action(p)
            lines.append(f"- **{p.name}** ({progress}%): {action}")
        if blocked:
            lines.extend(["", "## Blocked"])
            for p in blocked[:5]:
                lines.append(f"- {p.name}: {p.blockers or 'status blocked'}")
        if stale:
            lines.extend(["", "## Stale (no updates 14d+)"])
            for p in stale[:5]:
                lines.append(f"- {p.name}")
        return "\n".join(lines)
