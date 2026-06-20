"""Shared pytest fixtures for Rudra integration tests.

Design goals:
- Tests must NOT depend on a live Ollama / cloud LLM: the Brain and the embedding
  backend are stubbed so routing/command/research logic is exercised deterministically.
- DB-backed tests use the real local Postgres when available and skip cleanly otherwise.
"""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from rudra.brain.orchestrator import CompletionResult, ModelProvider
from rudra.main import app


@pytest.fixture(scope="session", autouse=True)
def _test_engine():
    """Use a NullPool engine for tests.

    The default QueuePool keeps asyncpg connections bound to the event loop that
    created them. Tests run across multiple loops (sync TestClient + per-test
    asyncio loops), so a pooled connection gets reused on the wrong loop and
    raises 'attached to a different loop'. NullPool opens/closes a fresh
    connection per session on the current loop, eliminating the conflict.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from rudra.core import database
    from rudra.core.config import get_settings

    database._engine = create_async_engine(
        get_settings().database_url, echo=False, poolclass=NullPool
    )
    database._session_factory = async_sessionmaker(
        database._engine, class_=AsyncSession, expire_on_commit=False
    )
    yield


@pytest.fixture(scope="session", autouse=True)
def _ensure_migrations(_test_engine):
    """Apply Alembic migrations when Postgres is reachable."""
    if not _db_reachable():
        return
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    backend = Path(__file__).resolve().parents[1]
    cfg = Config(str(backend / "alembic.ini"))
    command.upgrade(cfg, "head")


@pytest.fixture(autouse=True)
def _disable_ea_free_network(monkeypatch):
    """Avoid live HTTP from free EA connectors during the default test suite."""
    monkeypatch.setenv("ENABLE_EA_FREE_SOURCES", "false")
    monkeypatch.setenv("ENABLE_AGENT_FREE_SOURCES", "false")
    from rudra.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _high_rate_limit_for_tests(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10000")
    from rudra.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _disable_auth_by_default(monkeypatch, request):
    """Keep legacy tests working; test_auth.py enables auth in its own fixture."""
    is_auth_module = request.module.__name__.endswith("test_auth")
    if not is_auth_module:
        monkeypatch.setenv("AUTH_REQUIRED", "false")
        from rudra.core.config import get_settings

        get_settings.cache_clear()
    yield
    if not is_auth_module:
        from rudra.core.config import get_settings

        get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def stub_llm(monkeypatch):
    """Replace Brain.think with a deterministic local stub (no network)."""

    async def fake_think(self, messages, *, system=None, model_tier="default"):
        first = messages[0] if messages else None
        if first is None:
            content = ""
        elif hasattr(first, "content"):
            content = first.content
        elif isinstance(first, dict):
            content = first.get("content", "")
        else:
            content = str(first)
        lower = content.lower()
        if "analyze this user request against all nine" in lower:
            request_part = lower.split("request:")[-1] if "request:" in lower else lower
            selected = "executive_assistant"
            for token, agent in (
                ("research", "research_analyst"),
                ("travel", "travel"),
                ("writing", "writing"),
                ("presentation", "presentation"),
                ("luxury", "luxury_analyst"),
                ("concierge", "concierge"),
            ):
                if token in request_part:
                    selected = agent
                    break
            candidates = [
                {"agent": t.value, "score": 95 if t.value == selected else 40, "reason": "stub"}
                for t in __import__("rudra.agents.base", fromlist=["AgentType"]).AgentType
            ]
            import json

            return CompletionResult(
                content=json.dumps({"selected": selected, "candidates": candidates}),
                provider=ModelProvider.OLLAMA,
                model_id="stub",
            )
        if "classify this request" in lower:
            reply = "executive_assistant"
            for token in ("research", "travel", "writing", "presentation"):
                if token in lower.split("request:")[-1]:
                    mapping = {
                        "research": "research_analyst",
                        "travel": "travel",
                        "writing": "writing",
                        "presentation": "presentation",
                    }
                    reply = mapping[token]
                    break
            return CompletionResult(content=reply, provider=ModelProvider.OLLAMA, model_id="stub")
        return CompletionResult(
            content="STUB_RESPONSE: structured answer.",
            provider=ModelProvider.OLLAMA,
            model_id="stub",
        )

    monkeypatch.setattr("rudra.brain.orchestrator.Brain.think", fake_think)
    return fake_think


@pytest.fixture
def stub_embeddings(monkeypatch):
    """Return a deterministic 768-dim vector instead of calling Ollama/Gemini."""
    from rudra.core.config import get_settings

    dim = get_settings().embedding_dim

    async def fake_embed(text: str):
        # Deterministic pseudo-vector derived from text length; good enough for search wiring.
        seed = (len(text) % 7) + 1
        return [float((i * seed) % 10) / 10.0 for i in range(dim)]

    monkeypatch.setattr("rudra.brain.embeddings.embed_text", fake_embed)
    return fake_embed


def _db_reachable() -> bool:
    from rudra.core.database import get_session_factory
    from sqlalchemy import text

    async def _check() -> bool:
        try:
            factory = get_session_factory()
            async with factory() as s:
                await s.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    try:
        return asyncio.run(_check())
    except Exception:
        return False


@pytest.fixture(scope="session")
def db_available() -> bool:
    return _db_reachable()


@pytest.fixture
def require_db(db_available):
    if not db_available:
        pytest.skip("Postgres not reachable — skipping DB-backed test")
