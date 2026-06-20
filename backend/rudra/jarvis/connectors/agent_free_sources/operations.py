"""Agent 9 — Operations runbook free sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.free_sources import health_apis
from rudra.jarvis.connectors.free_sources._http import get_json


async def fetch_operations_intel(settings: Settings, query: str, *, limit: int = 8) -> list[IntelItem]:
    q = query or "maintenance safety recall"
    out: list[IntelItem] = []

    async def _openfda() -> None:
        for r in await health_apis.fetch_openfda_readings(limit=2):
            out.append(IntelItem(f"FDA signal: {r.metric_type}", f"{r.value} {r.unit or ''}", "openfda", "recall"))

    async def _cdc() -> None:
        for r in await health_apis.fetch_cdc_readings(limit=2):
            out.append(IntelItem(f"CDC {r.metric_type}", f"{r.value} {r.unit or ''}", "cdc", "health"))

    async def _datagov() -> None:
        data = await get_json(
            "https://catalog.data.gov/api/3/action/package_search",
            params={"q": "vendor contract maintenance", "rows": 3},
        )
        if isinstance(data, dict):
            for pkg in data.get("result", {}).get("results", [])[:3]:
                out.append(IntelItem(pkg.get("title", "Dataset")[:100], (pkg.get("notes") or "")[:160], "data.gov", "vendor"))

    async def _weather_ops() -> None:
        lat, lon = settings.ea_weather_lat, settings.ea_weather_lon
        data = await get_json(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "daily": "precipitation_sum", "forecast_days": 3},
        )
        if isinstance(data, dict):
            daily = data.get("daily", {})
            precip = daily.get("precipitation_sum", [])
            if precip:
                out.append(
                    IntelItem(
                        "3-day precipitation forecast",
                        f"Max daily mm: {max(precip):.1f}",
                        "open_meteo",
                        "maintenance",
                    )
                )

    async def _osha() -> None:
        data = await get_json(
            "https://www.osha.gov/ords/imis/establishment.search",
            params={"p_logger": "1", "establishment": q[:40]},
            timeout=10.0,
        )
        if data:
            out.append(IntelItem("OSHA establishment lookup", "Check OSHA IMIS for compliance context", "osha", "safety"))

    async def _wikidata_vendor() -> None:
        data = await get_json(
            "https://www.wikidata.org/w/api.php",
            params={"action": "wbsearchentities", "search": q[:50], "language": "en", "format": "json", "limit": 2},
        )
        if isinstance(data, dict):
            for hit in data.get("search", [])[:2]:
                out.append(IntelItem(hit.get("label", "Vendor")[:100], hit.get("description", "")[:140], "wikidata", "vendor"))

    await asyncio.gather(_openfda(), _cdc(), _datagov(), _weather_ops(), _osha(), _wikidata_vendor(), return_exceptions=True)
    return out[:limit]
