"""Agent 5 — Travel itinerary free sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.free_sources import travel_apis
from rudra.jarvis.connectors.free_sources._http import get_json


async def fetch_travel_intel(settings: Settings, query: str, *, limit: int = 8) -> list[IntelItem]:
    dest = query or settings.ea_weather_city or "Dubai"
    out: list[IntelItem] = []

    async def _restcountries() -> None:
        for t in await travel_apis.fetch_restcountries_travel(settings):
            out.append(IntelItem(t.title, t.location or "", t.provider or "restcountries", "visa"))

    async def _nominatim() -> None:
        for t in await travel_apis.fetch_nominatim_travel(settings):
            out.append(IntelItem(t.title, t.location or "", "nominatim", "geo"))

    async def _opensky() -> None:
        for t in await travel_apis.fetch_opensky_travel():
            out.append(IntelItem(t.title, t.location or "", "opensky", "flight"))

    async def _weather() -> None:
        lat, lon = settings.ea_weather_lat, settings.ea_weather_lon
        data = await get_json(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "current_weather": "true"},
        )
        if isinstance(data, dict):
            cw = data.get("current_weather", {})
            out.append(
                IntelItem(
                    f"Weather at {dest}",
                    f"{cw.get('temperature')}°C · wind {cw.get('windspeed')} km/h",
                    "open_meteo",
                    "weather",
                )
            )

    async def _visa_wiki() -> None:
        data = await get_json(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": f"visa requirements {dest}", "format": "json", "srlimit": 2},
        )
        if isinstance(data, dict):
            for hit in data.get("query", {}).get("search", [])[:2]:
                out.append(
                    IntelItem(
                        hit.get("title", "Visa info")[:120],
                        hit.get("snippet", "")[:180],
                        "wikipedia",
                        "visa",
                        f"https://en.wikipedia.org/wiki/{hit.get('title', '').replace(' ', '_')}",
                    )
                )

    async def _amadeus() -> None:
        for t in await travel_apis.fetch_amadeus_travel(settings):
            out.append(IntelItem(t.title, t.location or "", "amadeus", "deal"))

    await asyncio.gather(_restcountries(), _nominatim(), _opensky(), _weather(), _visa_wiki(), _amadeus(), return_exceptions=True)
    return out[:limit]
