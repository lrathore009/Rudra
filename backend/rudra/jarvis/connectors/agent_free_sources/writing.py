"""Agent 7 — Writing draft studio free sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.free_sources._http import get_json


async def fetch_writing_intel(settings: Settings, query: str, *, limit: int = 6) -> list[IntelItem]:
    q = query or "communication"
    out: list[IntelItem] = []

    async def _datamuse() -> None:
        words = q.split()[:2]
        for word in words:
            data = await get_json("https://api.datamuse.com/words", params={"ml": word, "max": 5})
            if isinstance(data, list) and data:
                syns = ", ".join(d.get("word", "") for d in data[:5])
                out.append(IntelItem(f"Synonyms for '{word}'", syns, "datamuse", "vocabulary"))

    async def _quotable() -> None:
        data = await get_json("https://api.quotable.io/quotes/random", params={"limit": 2})
        items = data if isinstance(data, list) else [data] if isinstance(data, dict) else []
        for qte in items[:2]:
            if isinstance(qte, dict):
                out.append(
                    IntelItem(
                        qte.get("content", "")[:120],
                        f"— {qte.get('author', 'Unknown')}",
                        "quotable",
                        "quote",
                    )
                )

    async def _wikipedia_style() -> None:
        data = await get_json(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "opensearch", "search": f"{q} writing style", "limit": 2, "format": "json"},
        )
        if isinstance(data, list) and len(data) >= 4:
            for title, desc, url in zip(data[1], data[2], data[3]):
                out.append(IntelItem(title[:100], desc[:160], "wikipedia", "reference", url))

    async def _news_context() -> None:
        from rudra.jarvis.connectors.free_sources import news_apis

        for h in await news_apis.fetch_gdelt_headlines(limit=2):
            out.append(IntelItem(h.title, h.source, "gdelt", "context", h.url))

    await asyncio.gather(_datamuse(), _quotable(), _wikipedia_style(), _news_context(), return_exceptions=True)
    return out[:limit]
