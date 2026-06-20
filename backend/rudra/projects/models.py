"""Project OS domain models."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from rudra.memory.models.base import Base, TimestampMixin, UUIDMixin


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class FounderProject(Base, UUIDMixin, TimestampMixin):
    """Extended project record for Founder OS (separate from legacy projects table)."""

    __tablename__ = "founder_projects"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(256), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=ProjectStatus.ACTIVE.value, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    repo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    live_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    blockers: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class ProjectMilestone(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "project_milestones"

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("founder_projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    completed: Mapped[bool] = mapped_column(default=False)


class ProjectTask(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "project_tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("founder_projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="todo")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    due_date: Mapped[str | None] = mapped_column(String(32), nullable=True)


class ProjectUpdate(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "project_updates"

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("founder_projects.id", ondelete="CASCADE"), index=True)
    summary: Mapped[str] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(128), nullable=True)


class ProjectMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "project_metrics"

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("founder_projects.id", ondelete="CASCADE"), index=True)
    metric_key: Mapped[str] = mapped_column(String(64))
    metric_value: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
