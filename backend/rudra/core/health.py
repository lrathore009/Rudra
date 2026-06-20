"""Service health checks for Postgres, Redis, Qdrant, and Ollama.

Every check is best-effort and never raises: a downed optional service should
degrade Rudra, not crash it. Each returns a small status dict.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
from sqlalchemy import text

from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)

_TIMEOUT = 3.0


async def check_postgres() -> dict[str, Any]:
    """Verify the primary datastore (Postgres + pgvector) responds to a query."""
    from rudra.core.database import get_session_factory

    try:
        factory = get_session_factory()
        async with factory() as session:
            await asyncio.wait_for(session.execute(text("SELECT 1")), timeout=_TIMEOUT)
            has_vector = await session.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            pgvector = has_vector.scalar() is not None
        return {"service": "postgres", "ok": True, "detail": {"pgvector": pgvector}}
    except Exception as e:  # noqa: BLE001
        return {"service": "postgres", "ok": False, "error": str(e)[:160]}


async def check_redis() -> dict[str, Any]:
    """Optional cache/queue. Down is acceptable in Phase 1."""
    settings = get_settings()
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.redis_url)
        try:
            pong = await asyncio.wait_for(client.ping(), timeout=_TIMEOUT)
        finally:
            await client.aclose()
        return {"service": "redis", "ok": bool(pong), "optional": True}
    except Exception as e:  # noqa: BLE001
        return {"service": "redis", "ok": False, "optional": True, "error": str(e)[:160]}


async def check_qdrant() -> dict[str, Any]:
    """Optional vector DB. pgvector is the active store, so Qdrant is optional."""
    settings = get_settings()
    url = f"http://{settings.qdrant_host}:{settings.qdrant_port}/readyz"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url)
        return {"service": "qdrant", "ok": resp.status_code == 200, "optional": True}
    except Exception as e:  # noqa: BLE001
        return {"service": "qdrant", "ok": False, "optional": True, "error": str(e)[:160]}


async def check_ollama() -> dict[str, Any]:
    """Local LLM runtime. Reports installed models when reachable."""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            resp.raise_for_status()
            models = [m.get("name", "") for m in resp.json().get("models", [])]
        return {
            "service": "ollama",
            "ok": True,
            "detail": {"models": models, "chat_model": settings.ollama_chat_model},
        }
    except Exception as e:  # noqa: BLE001
        return {"service": "ollama", "ok": False, "error": str(e)[:160]}


def check_llm_config() -> dict[str, Any]:
    """Report which LLM providers are configured (key present / local available)."""
    settings = get_settings()
    return {
        "service": "llm",
        "ok": True,
        "detail": {
            "gemini": settings.google_ai_api_key is not None,
            "openai": settings.openai_api_key is not None,
            "anthropic": settings.anthropic_api_key is not None,
            "ollama": True,  # local fallback always attempted
        },
    }


async def gather_health() -> dict[str, Any]:
    """Run all checks concurrently and summarize overall readiness."""
    pg, redis_s, qdrant_s, ollama_s = await asyncio.gather(
        check_postgres(),
        check_redis(),
        check_qdrant(),
        check_ollama(),
    )
    llm = check_llm_config()
    services = [pg, redis_s, qdrant_s, ollama_s, llm]

    # Required for core function: Postgres + at least one usable LLM (Ollama or a cloud key).
    has_llm = ollama_s["ok"] or any(llm["detail"][p] for p in ("gemini", "openai", "anthropic"))
    required_ok = pg["ok"] and has_llm

    return {
        "status": "operational" if required_ok else "degraded",
        "required_ok": required_ok,
        "services": services,
    }
