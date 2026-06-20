"""SQLAlchemy models for agent phases 3–9."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from rudra.memory.models.base import Base, TimestampMixin, UUIDMixin


class RetrievalTrace(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "retrieval_traces"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    query: Mapped[str] = mapped_column(Text)
    answer_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    sources: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)


class ConciergeRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "concierge_requests"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(512))
    details: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="requested")
    venue_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    party_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scheduled_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class TravelTrip(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "travel_trips"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="planning")
    project_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class TravelLeg(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "travel_legs"

    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    user_id: Mapped[str] = mapped_column(String(128))
    sequence: Mapped[int] = mapped_column(Integer, default=1)
    origin: Mapped[str | None] = mapped_column(String(256), nullable=True)
    destination: Mapped[str] = mapped_column(String(256))
    starts_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ends_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    checklist: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="planned")
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class LuxuryIntelSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "luxury_intel_snapshots"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    subject: Mapped[str] = mapped_column(String(512))
    category: Mapped[str] = mapped_column(String(64))
    briefing: Mapped[str] = mapped_column(Text)
    exclusivity_score: Mapped[float] = mapped_column(Float, default=0.5)
    investment_relevance: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class LuxuryAlert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "luxury_alerts"

    user_id: Mapped[str] = mapped_column(String(128))
    watchlist_title: Mapped[str] = mapped_column(String(512))
    alert_type: Mapped[str] = mapped_column(String(64), default="price_change")
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_triggered: Mapped[str | None] = mapped_column(String(64), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class WritingDraft(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "writing_drafts"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    format: Mapped[str] = mapped_column(String(32), default="email")
    tone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class WritingDraftVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "writing_draft_versions"

    draft_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    version: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)


class PresentationDeck(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "presentation_decks"

    user_id: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(512))
    audience: Mapped[str] = mapped_column(String(128), default="executive")
    status: Mapped[str] = mapped_column(String(32), default="draft")
    slide_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class PresentationSlide(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "presentation_slides"

    deck_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    sequence: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    speaker_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sources: Mapped[list | None] = mapped_column(JSONB, nullable=True)


class OpsSlaEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ops_sla_events"

    user_id: Mapped[str] = mapped_column(String(128))
    vendor_name: Mapped[str] = mapped_column(String(256))
    event_type: Mapped[str] = mapped_column(String(64))
    due_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class VendorInteraction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "vendor_interactions"

    user_id: Mapped[str] = mapped_column(String(128))
    vendor_name: Mapped[str] = mapped_column(String(256))
    interaction_type: Mapped[str] = mapped_column(String(64), default="contact")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
