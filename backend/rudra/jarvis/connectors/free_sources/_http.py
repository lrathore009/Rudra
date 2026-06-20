"""Shared HTTP helpers for free EA source connectors."""

from __future__ import annotations

import httpx

from rudra.core.logging import get_logger

logger = get_logger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Rudra/0.1 EA (local-first; research@rudra.local)",
    "Accept": "application/json",
}


async def get_json(url: str, *, params: dict | None = None, headers: dict | None = None, timeout: float = 12.0) -> dict | list | None:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            r = await client.get(url, params=params, headers={**DEFAULT_HEADERS, **(headers or {})})
            if r.status_code != 200:
                return None
            return r.json()
    except Exception as e:  # noqa: BLE001
        logger.debug("free_source_http_failed", url=url[:80], error=str(e)[:100])
        return None


async def get_text(url: str, *, timeout: float = 12.0) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            r = await client.get(url, headers=DEFAULT_HEADERS)
            if r.status_code != 200:
                return None
            return r.text
    except Exception as e:  # noqa: BLE001
        logger.debug("free_source_text_failed", url=url[:80], error=str(e)[:100])
        return None
