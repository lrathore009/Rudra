"""Knowledge graph domain models."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Float, ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rudra.memory.models.base import Base, TimestampMixin, UUIDMixin


class EntityType(str, enum.Enum):
    PERSON = "person"
    COMPANY = "company"
    PROJECT = "project"
    APP = "app"
    DOCUMENT = "document"
    BOOK = "book"
    TOPIC = "topic"
    GOAL = "goal"
    TASK = "task"
    DECISION = "decision"
    EVENT = "event"


class GraphRelationType(str, enum.Enum):
    OWNS = "owns"
    WORKS_ON = "works_on"
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"
    INSPIRED_BY = "inspired_by"
    PART_OF = "part_of"
    MENTIONS = "mentions"
    BLOCKED_BY = "blocked_by"
    COMPLETED = "completed"


class Entity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "entities"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(256), index=True)
    entity_type: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    aliases: Mapped[list["EntityAlias"]] = relationship(back_populates="entity", cascade="all, delete-orphan")


class EntityAlias(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "entity_aliases"

    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    alias: Mapped[str] = mapped_column(String(256), index=True)

    entity: Mapped[Entity] = relationship(back_populates="aliases")


class GraphRelationship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "graph_relationships"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    target_entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    relation_type: Mapped[str] = mapped_column(String(64), index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class MemoryEntityLink(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "memory_entity_links"

    memory_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("memories.id", ondelete="CASCADE"), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    relation_type: Mapped[str] = mapped_column(String(64), default=GraphRelationType.MENTIONS.value)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)


class ProjectEntityLink(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "project_entity_links"

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    relation_type: Mapped[str] = mapped_column(String(64), default=GraphRelationType.RELATED_TO.value)
