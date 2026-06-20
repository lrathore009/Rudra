"""Authentication service — login, user bootstrap, token issuance."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.auth.models import User
from rudra.core.config import get_settings
from rudra.security.audit import AuditAction, log_audit
from rudra.security.encryption import TokenService, hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tokens = TokenService()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.external_id == external_id))
        return result.scalar_one_or_none()

    async def ensure_owner_user(self) -> User:
        settings = get_settings()
        existing = await self.get_by_username(settings.owner_username)
        password = settings.owner_password.get_secret_value()
        if existing:
            if not verify_password(password, existing.password_hash):
                existing.password_hash = hash_password(password)
            return existing
        user = User(
            username=settings.owner_username,
            display_name="Owner",
            password_hash=hash_password(settings.owner_password.get_secret_value()),
            is_active=True,
            is_owner=True,
            external_id="owner",
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def login(
        self,
        username: str,
        password: str,
        *,
        ip_address: str | None = None,
    ) -> tuple[str, User] | None:
        user = await self.get_by_username(username)
        if user is None or not user.is_active:
            await log_audit(
                self.session,
                AuditAction.LOGIN_FAILED,
                actor_id=username,
                outcome="failure",
                ip_address=ip_address,
                details={"reason": "invalid_credentials"},
            )
            return None
        if not verify_password(password, user.password_hash):
            await log_audit(
                self.session,
                AuditAction.LOGIN_FAILED,
                actor_id=user.external_id,
                outcome="failure",
                ip_address=ip_address,
                details={"reason": "invalid_credentials"},
            )
            return None
        token = self.tokens.create_token(user.external_id, {"username": user.username})
        await log_audit(
            self.session,
            AuditAction.LOGIN,
            actor_id=user.external_id,
            outcome="success",
            ip_address=ip_address,
        )
        return token, user

    async def logout(self, user_id: str, *, ip_address: str | None = None) -> None:
        await log_audit(
            self.session,
            AuditAction.LOGOUT,
            actor_id=user_id,
            outcome="success",
            ip_address=ip_address,
        )

    def user_id(self, user: User) -> str:
        return user.external_id
