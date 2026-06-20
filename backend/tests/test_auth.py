"""Authentication and API hardening tests."""

import pytest
from sqlalchemy import select

from rudra.core.config import get_settings
from rudra.security.audit import AuditAction, AuditLog


@pytest.fixture(autouse=True)
def _auth_enabled(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("OWNER_USERNAME", "owner")
    monkeypatch.setenv("OWNER_PASSWORD", "test_pass_123")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _login(client, username="owner", password="test_pass_123") -> str:
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_login_success(client, require_db):
    token = _login(client)
    assert isinstance(token, str) and len(token) > 20


def test_login_failure(client, require_db):
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "owner", "password": "wrong-password"},
    )
    assert res.status_code == 401


def test_protected_route_blocked_without_token(client, require_db):
    res = client.post("/api/v1/command", json={"command": "hello"})
    assert res.status_code == 401


def test_protected_route_allowed_with_token(client, require_db, stub_llm, stub_embeddings):
    token = _login(client)
    res = client.post(
        "/api/v1/command",
        json={"command": "hello", "auto_route": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert "response" in res.json()


def test_rate_limit(monkeypatch):
    """Unit test sliding-window limiter (in-process state persists across TestClient calls)."""
    from collections import deque

    from rudra.core.middleware import RateLimitMiddleware

    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")
    get_settings.cache_clear()

    mw = RateLimitMiddleware(app=None, requests_per_minute=2)
    mw._hits.clear()
    key = "127.0.0.1:v1:skills"
    assert mw._allow(key, 2) is True
    assert mw._allow(key, 2) is True
    assert mw._allow(key, 2) is False


@pytest.mark.asyncio
async def test_audit_log_on_login(client, require_db):
    _login(client)
    from rudra.core.database import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(AuditLog)
            .where(AuditLog.action == AuditAction.LOGIN.value)
            .order_by(AuditLog.timestamp.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        assert row is not None
        assert row.outcome == "success"
