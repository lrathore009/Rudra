"""API dependencies — auth, user context."""

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.core.config import get_settings
from rudra.core.database import get_db
from rudra.security.audit import AuditAction, log_audit
from rudra.security.encryption import TokenService

DEFAULT_USER_ID = "owner"


async def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Extract user ID from JWT. Falls back to owner only when auth is disabled."""
    settings = get_settings()

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        payload = TokenService().verify_token(token)
        if payload and payload.get("sub"):
            return str(payload["sub"])

    if not settings.auth_required:
        return DEFAULT_USER_ID

    await log_audit(
        db,
        AuditAction.AUTH_DENIED,
        actor_id="anonymous",
        outcome="failure",
        ip_address=request.client.host if request.client else None,
        details={"path": request.url.path},
    )
    raise HTTPException(status_code=401, detail="Authentication required")


async def require_auth(user_id: str = Depends(get_current_user)) -> str:
    return user_id
