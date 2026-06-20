"""Domain models for agent phase encoded data."""

from typing import Any

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from rudra.memory.models.base import Base, TimestampMixin, UUIDMixin


class AgentArtifact(Base, UUIDMixin, TimestampMixin):
    """Structured domain record owned by a specialist agent phase."""

    __tablename__ = "agent_artifacts"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    agent_type: Mapped[str] = mapped_column(String(64), index=True)
    artifact_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
