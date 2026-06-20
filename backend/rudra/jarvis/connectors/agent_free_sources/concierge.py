"""Agent 3 — Experience Concierge free sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.free_sources._http import get_json, get_text
import xml.etree.ElementTree as ET


async def fetch_concierge_intel(settings: Settings, query: str, *, limit: int = 8) -> list[IntelItem]:
    city = settings.ea_weather_city or "Dubai"
    q = query or f"fine dining {city}"
    out: list[IntelItem] = []

    async def _nominatim() -> None:
        data = await get_json(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"restaurant {city}", "format": "json", "limit": 4},
            headers={"User-Agent": "Rudra/0.1 Concierge"},
        )
        if isinstance(data, list):
            for hit in data[:4]:
                out.append(
                    IntelItem(
                        hit.get("display_name", "Venue")[:100],
                        f"OSM venue · {hit.get('type', 'place')}",
                        "nominatim",
                        "venue",
                    )
                )

    async def _wikidata() -> None:
        data = await get_json(
            "https://www.wikidata.org/w/api.php",
            params={"action": "wbsearchentities", "search": q[:60], "language": "en", "format": "json", "limit": 3},
        )
        if isinstance(data, dict):
            for hit in data.get("search", [])[:3]:
                out.append(
                    IntelItem(
                        hit.get("label", "Venue")[:100],
                        hit.get("description", "Wikidata entity")[:160],
                        "wikidata",
                        "venue",
                    )
                )

    async def _food_rss() -> None:
        feeds = [
            "https://www.eater.com/rss/index.xml",
            "https://www.theworlds50best.com/feed/",
        ]
        for url in feeds:
            text = await get_text(url, timeout=8.0)
            if not text:
                continue
            try:
                root = ET.fromstring(text)
                for item in root.findall(".//item")[:2]:
                    title = (item.findtext("title") or "").strip()
                    if title:
                        out.append(IntelItem(title[:120], "Food & dining RSS", "food_rss", "dining", item.findtext("link")))
            except Exception:
                continue

    async def _yelp() -> None:
        key = getattr(settings, "yelp_api_key", None)
        if not key:
            return
        data = await get_json(
            "https://api.yelp.com/v3/businesses/search",
            params={"term": "restaurants", "location": city, "limit": 3},
            headers={"Authorization": f"Bearer {key}"},
        )
        if isinstance(data, dict):
            for b in data.get("businesses", [])[:3]:
                out.append(
                    IntelItem(
                        b.get("name", "Restaurant")[:100],
                        f"Yelp {b.get('rating', '?')}★ · {b.get('review_count', 0)} reviews",
                        "yelp",
                        "dining",
                        b.get("url"),
                    )
                )

    await asyncio.gather(_nominatim(), _wikidata(), _food_rss(), _yelp(), return_exceptions=True)
    return out[:limit]
