"""Immutable audit logging for zero-trust compliance."""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from rudra.memory.models.base import Base


class AuditAction(str, Enum):
    LOGIN = "login"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    COMMAND_EXECUTE = "command_execute"
    MEMORY_CREATE = "memory_create"
    MEMORY_READ = "memory_read"
    MEMORY_UPDATE = "memory_update"
    MEMORY_DELETE = "memory_delete"
    AGENT_INVOKE = "agent_invoke"
    RESEARCH_START = "research_start"
    RESEARCH_COMPLETE = "research_complete"
    SECRET_ACCESS = "secret_access"
    EXPORT_DATA = "export_data"
    DELETE_DATA = "delete_data"
    SETTINGS_CHANGE = "settings_change"
    DOCUMENT_UPLOAD = "document_upload"
    AUTH_DENIED = "auth_denied"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )
    action: Mapped[str] = mapped_column(String(64), index=True)
    actor_id: Mapped[str] = mapped_column(String(128), index=True)
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    outcome: Mapped[str] = mapped_column(String(32), default="success")
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)


async def log_audit(
    session,
    action: AuditAction,
    actor_id: str,
    *,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    outcome: str = "success",
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        action=action.value,
        actor_id=actor_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        outcome=outcome,
        ip_address=ip_address,
    )
    session.add(entry)
    await session.flush()
    return entry
