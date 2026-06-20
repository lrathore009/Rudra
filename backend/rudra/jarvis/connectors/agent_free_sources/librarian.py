"""Agent 6 — Knowledge Librarian free sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.free_sources._http import get_json


async def fetch_librarian_intel(settings: Settings, query: str, *, limit: int = 8) -> list[IntelItem]:
    q = query or settings.ea_knowledge_topics.split(",")[0].strip() or "knowledge"
    out: list[IntelItem] = []

    async def _wikidata_sparql() -> None:
        data = await get_json(
            "https://www.wikidata.org/w/api.php",
            params={"action": "wbsearchentities", "search": q, "language": "en", "format": "json", "limit": 4},
        )
        if isinstance(data, dict):
            for hit in data.get("search", [])[:4]:
                out.append(
                    IntelItem(
                        hit.get("label", q)[:100],
                        hit.get("description", "Wikidata")[:180],
                        "wikidata",
                        "entity",
                        f"https://www.wikidata.org/wiki/{hit.get('id', '')}",
                    )
                )

    async def _dbpedia() -> None:
        data = await get_json(
            "https://lookup.dbpedia.org/api/search",
            params={"query": q, "format": "json", "maxResults": 3},
        )
        if isinstance(data, dict):
            for doc in data.get("docs", [])[:3]:
                out.append(IntelItem(doc.get("label", q)[:100], "DBpedia lookup", "dbpedia", "entity"))

    async def _openalex() -> None:
        data = await get_json("https://api.openalex.org/works", params={"search": q, "per_page": 3})
        if isinstance(data, dict):
            for w in data.get("results", [])[:3]:
                out.append(IntelItem((w.get("title") or q)[:120], "OpenAlex work", "openalex", "reference", w.get("id")))

    async def _europeana() -> None:
        key = getattr(settings, "europeana_api_key", None)
        params = {"query": q, "rows": 3}
        if key:
            params["wskey"] = key
        data = await get_json("https://api.europeana.eu/record/v2/search.json", params=params)
        if isinstance(data, dict):
            for item in data.get("items", [])[:3]:
                out.append(
                    IntelItem(
                        item.get("title", ["Item"])[0][:100] if isinstance(item.get("title"), list) else str(item.get("title", "Item"))[:100],
                        "Europeana cultural heritage",
                        "europeana",
                        "archive",
                    )
                )

    async def _loc() -> None:
        data = await get_json(
            "https://www.loc.gov/search/",
            params={"q": q, "fo": "json", "c": 3},
        )
        if isinstance(data, dict):
            for r in data.get("results", [])[:3]:
                out.append(IntelItem(r.get("title", "LOC item")[:100], r.get("description", "Library of Congress")[:160], "loc", "archive", r.get("url")))

    async def _gutenberg() -> None:
        data = await get_json("https://gutendex.com/books/", params={"search": q[:40]})
        if isinstance(data, dict):
            for book in data.get("results", [])[:2]:
                title = book.get("title", "Book")[:100]
                out.append(IntelItem(title, "Project Gutenberg", "gutenberg", "book"))

    await asyncio.gather(_wikidata_sparql(), _dbpedia(), _openalex(), _europeana(), _loc(), _gutenberg(), return_exceptions=True)
    return out[:limit]
