"""Jarvis layer persistence models."""

from typing import Any

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from rudra.memory.models.base import Base, TimestampMixin, UUIDMixin


class ConnectorToken(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "connector_tokens"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    tokens: Mapped[dict[str, Any]] = mapped_column(JSONB)


class OperatorState(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "operator_states"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    operator_id: Mapped[str] = mapped_column(String(128), index=True)
    state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    last_tick: Mapped[str | None] = mapped_column(Text, nullable=True)


class FederationDevice(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "federation_devices"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    device_id: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    device_label: Mapped[str] = mapped_column(String(256), default="device")
    sync_token: Mapped[str] = mapped_column(String(512))
    last_sync_at: Mapped[str | None] = mapped_column(Text, nullable=True)
