"""Research library auxiliary models — watchlist and job telemetry."""

from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from rudra.memory.models.base import Base, TimestampMixin, UUIDMixin


class ResearchWatchlist(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_watchlist"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    topic: Mapped[str] = mapped_column(String(256))
    query_template: Mapped[str] = mapped_column(Text)
    ttl_days: Mapped[int] = mapped_column(Integer, default=30)
    last_run_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_report_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class ResearchJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_jobs"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    query: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    report_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    telemetry_: Mapped[dict | None] = mapped_column("telemetry", JSONB, nullable=True)
