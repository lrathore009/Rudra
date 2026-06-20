"""Agent 8 — Presentation deck builder free sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.free_sources._http import get_json


async def fetch_presentation_intel(settings: Settings, query: str, *, limit: int = 8) -> list[IntelItem]:
    q = query or settings.ea_knowledge_topics.split(",")[0].strip() or "business trends"
    out: list[IntelItem] = []

    async def _owid() -> None:
        data = await get_json("https://api.ourworldindata.org/v1/indicators", timeout=15.0)
        if isinstance(data, list):
            for ind in data[:3]:
                name = ind.get("name") or ind.get("slug", "Indicator")
                out.append(IntelItem(name[:100], "Our World in Data indicator", "owid", "chart"))

    async def _worldbank() -> None:
        data = await get_json(
            "https://api.worldbank.org/v2/country/all/indicator/SL.UEM.TOTL.ZS",
            params={"format": "json", "per_page": 2, "date": "2023:2024"},
        )
        if isinstance(data, list) and len(data) > 1:
            for row in data[1][:2]:
                out.append(
                    IntelItem(
                        f"Unemployment {row.get('country', {}).get('value', '?')}",
                        f"{row.get('value')}%",
                        "worldbank",
                        "stat",
                    )
                )

    async def _nasa() -> None:
        data = await get_json(
            "https://api.nasa.gov/planetary/apod",
            params={"api_key": settings.nasa_api_key or "DEMO_KEY"},
        )
        if isinstance(data, dict) and data.get("title"):
            out.append(
                IntelItem(
                    data["title"][:100],
                    (data.get("explanation") or "")[:200],
                    "nasa",
                    "visual",
                    data.get("url"),
                )
            )

    async def _openalex() -> None:
        data = await get_json("https://api.openalex.org/works", params={"search": q, "per_page": 3})
        if isinstance(data, dict):
            for w in data.get("results", [])[:3]:
                out.append(IntelItem((w.get("title") or q)[:120], "Slide source candidate", "openalex", "research", w.get("id")))

    async def _unsplash() -> None:
        key = getattr(settings, "unsplash_access_key", None)
        if not key:
            return
        data = await get_json(
            "https://api.unsplash.com/search/photos",
            params={"query": q[:40], "per_page": 2},
            headers={"Authorization": f"Client-ID {key}"},
        )
        if isinstance(data, dict):
            for photo in data.get("results", [])[:2]:
                out.append(
                    IntelItem(
                        photo.get("description") or photo.get("alt_description") or "Photo",
                        "Unsplash visual",
                        "unsplash",
                        "visual",
                        photo.get("links", {}).get("html"),
                    )
                )

    await asyncio.gather(_owid(), _worldbank(), _nasa(), _openalex(), _unsplash(), return_exceptions=True)
    return out[:limit]
