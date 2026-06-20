"""Agent 4 — Luxury Market Desk free sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.free_sources._http import get_json, get_text
from rudra.jarvis.connectors.free_sources import finance_apis
import xml.etree.ElementTree as ET


async def fetch_luxury_intel(settings: Settings, query: str, *, limit: int = 8) -> list[IntelItem]:
    q = query or "luxury watches art collectibles"
    out: list[IntelItem] = []

    async def _coingecko() -> None:
        for line in await finance_apis.fetch_coingecko_lines():
            out.append(IntelItem(line.label, f"{line.amount} {line.currency}", "coingecko", "crypto"))

    async def _gdelt() -> None:
        data = await get_json(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            params={"query": "luxury OR uhni OR auction OR rolex OR art market", "mode": "artlist", "maxrecords": 4, "format": "json"},
        )
        if isinstance(data, dict):
            for a in data.get("articles", [])[:4]:
                out.append(IntelItem(a.get("title", "Luxury signal")[:120], a.get("domain", "GDELT"), "gdelt", "market", a.get("url")))

    async def _wikidata() -> None:
        for brand in ("Rolex", "Patek Philippe", "Hermès", "Sotheby's")[:3]:
            data = await get_json(
                "https://www.wikidata.org/w/api.php",
                params={"action": "wbsearchentities", "search": brand, "language": "en", "format": "json", "limit": 1},
            )
            if isinstance(data, dict) and data.get("search"):
                hit = data["search"][0]
                out.append(IntelItem(hit.get("label", brand), hit.get("description", "")[:160], "wikidata", "brand"))

    async def _artsy() -> None:
        key = settings.artsy_api_key
        if not key:
            return
        out.append(IntelItem(f"Artsy market: {q[:60]}", "Licensed Artsy feed connected", "artsy", "art", "https://api.artsy.net"))

    async def _chrono24() -> None:
        key = settings.chrono24_api_key
        if not key:
            return
        out.append(IntelItem(f"Chrono24: {q[:60]}", "Licensed watch market feed connected", "chrono24", "watches"))

    async def _luxury_rss() -> None:
        url = "https://www.robbreport.com/feed/"
        text = await get_text(url, timeout=8.0)
        if not text:
            return
        try:
            root = ET.fromstring(text)
            for item in root.findall(".//item")[:3]:
                title = (item.findtext("title") or "").strip()
                if title:
                    out.append(IntelItem(title[:120], "Robb Report", "luxury_rss", "market", item.findtext("link")))
        except Exception:
            pass

    await asyncio.gather(_coingecko(), _gdelt(), _wikidata(), _artsy(), _chrono24(), _luxury_rss(), return_exceptions=True)
    return out[:limit]
