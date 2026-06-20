"""Memory layer models — episodic, semantic, project, preference, relationship, research."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pgvector.sqlalchemy import Vector
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rudra.core.config import get_settings
from rudra.memory.models.base import Base, TimestampMixin, UUIDMixin

# Vector dimension follows the configured (free) embedding model: 768 for
# nomic-embed-text (Ollama) and text-embedding-004 (Gemini).
EMBEDDING_DIM = get_settings().embedding_dim


class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROJECT = "project"
    PREFERENCE = "preference"
    RELATIONSHIP = "relationship"
    RESEARCH = "research"


class Memory(Base, UUIDMixin, TimestampMixin):
    """Core memory unit — all intelligence accumulates here."""

    __tablename__ = "memories"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    memory_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    tags: Mapped[list["MemoryTag"]] = relationship(back_populates="memory", cascade="all, delete-orphan")
    links: Mapped[list["MemoryLink"]] = relationship(
        "MemoryLink",
        foreign_keys="MemoryLink.source_id",
        back_populates="source",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_memories_user_type", "user_id", "memory_type"),
        Index("ix_memories_importance", "importance"),
    )


class MemoryTag(Base, UUIDMixin):
    __tablename__ = "memory_tags"

    memory_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("memories.id", ondelete="CASCADE"))
    tag: Mapped[str] = mapped_column(String(128), index=True)
    memory: Mapped["Memory"] = relationship(back_populates="tags")


class MemoryLink(Base, UUIDMixin, TimestampMixin):
    """Knowledge graph edges between memories."""

    __tablename__ = "memory_links"

    source_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("memories.id", ondelete="CASCADE"))
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("memories.id", ondelete="CASCADE"))
    relation_type: Mapped[str] = mapped_column(String(64))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped["Memory"] = relationship(foreign_keys=[source_id], back_populates="links")


class Project(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "projects"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)


class Preference(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "preferences"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(128), index=True)
    key: Mapped[str] = mapped_column(String(256))
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[str | None] = mapped_column(String(256), nullable=True)


class Relationship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "relationships"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(256))
    relation_type: Mapped[str] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    last_interaction: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ResearchReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_reports"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(512))
    query: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    citations: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    sources: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    topic_tags: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    query_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
