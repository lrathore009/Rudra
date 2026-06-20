"""Integration foundation models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from rudra.memory.models.base import Base, TimestampMixin, UUIDMixin


class Integration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integrations"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="disconnected")
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class ExternalAccount(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "external_accounts"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    provider: Mapped[str] = mapped_column(String(64))
    account_label: Mapped[str] = mapped_column(String(256))
    connected: Mapped[bool] = mapped_column(Boolean, default=False)


class ExternalEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "external_events"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    provider: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    starts_at: Mapped[str] = mapped_column(String(64))
    ends_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class ExternalEmail(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "external_emails"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    provider: Mapped[str] = mapped_column(String(64))
    sender: Mapped[str] = mapped_column(String(256))
    subject: Mapped[str] = mapped_column(String(512))
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[str] = mapped_column(String(64))
    needs_attention: Mapped[bool] = mapped_column(Boolean, default=False)


class DailyBriefing(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "daily_briefings"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    briefing_date: Mapped[str] = mapped_column(String(32), index=True)
    content: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class EACommitment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ea_commitments"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(512))
    owner: Mapped[str | None] = mapped_column(String(256), nullable=True)
    due_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    source_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class EAFeedItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ea_feed_items"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(512))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(64))
    external_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EAFinanceSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ea_finance_snapshots"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    snapshot_date: Mapped[str] = mapped_column(String(32), index=True)
    label: Mapped[str] = mapped_column(String(256))
    amount: Mapped[float] = mapped_column()
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class EAHealthMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ea_health_metrics"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    metric_date: Mapped[str] = mapped_column(String(32), index=True)
    metric_type: Mapped[str] = mapped_column(String(64))
    value: Mapped[float] = mapped_column()
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class EATranscript(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ea_transcripts"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    meeting_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    action_items: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    provider: Mapped[str] = mapped_column(String(64), default="manual")
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
