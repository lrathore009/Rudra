"""Health free sources — OpenFDA, PubMed, CDC, health export CSV."""

from __future__ import annotations

import csv
from pathlib import Path

from rudra.core.config import Settings
from rudra.integrations.providers import HealthReading
from rudra.jarvis.connectors.free_sources._http import get_json


async def fetch_openfda_readings(*, limit: int = 3) -> list[HealthReading]:
    data = await get_json("https://api.fda.gov/drug/event.json", params={"limit": limit})
    if not isinstance(data, dict):
        return []
    results = data.get("results", [])
    return [
        HealthReading(
            "fda_adverse_event",
            float(len(r.get("patient", {}).get("drug", [])) or 1),
            "reports",
            r.get("receivedate"),
        )
        for r in results[:limit]
    ]


async def fetch_pubmed_readings(*, query: str = "public health", limit: int = 3) -> list[HealthReading]:
    search = await get_json(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        params={"db": "pubmed", "term": query, "retmode": "json", "retmax": limit},
    )
    if not isinstance(search, dict):
        return []
    ids = search.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    summary = await get_json(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
    )
    if not isinstance(summary, dict):
        return []
    result = summary.get("result", {})
    out: list[HealthReading] = []
    for pid in ids:
        item = result.get(pid, {})
        title = (item.get("title") or "PubMed article")[:60]
        out.append(HealthReading("pubmed", 1.0, title, item.get("pubdate")))
    return out[:limit]


async def fetch_cdc_readings(*, limit: int = 3) -> list[HealthReading]:
    data = await get_json(
        "https://data.cdc.gov/resource/gkpt-pn9h.json",
        params={"$limit": limit, "$order": "date desc"},
        timeout=15.0,
    )
    if not isinstance(data, list):
        return []
    return [
        HealthReading(
            "cdc_wastewater",
            float(row.get("percentile") or 0),
            "percentile",
            row.get("date"),
        )
        for row in data[:limit]
        if row.get("date")
    ]


async def fetch_health_export_readings(settings: Settings) -> list[HealthReading]:
    path = settings.ea_health_export_path
    if not path:
        return []
    file = Path(path)
    if not file.is_file():
        return []
    out: list[HealthReading] = []
    try:
        with file.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in list(reader)[-10:]:
                metric = row.get("metric_type") or row.get("type") or row.get("Metric")
                value = row.get("value") or row.get("Value")
                unit = row.get("unit") or row.get("Unit")
                date = row.get("date") or row.get("Date") or row.get("Start")
                if metric and value:
                    out.append(HealthReading(metric[:40], float(value), unit, date))
    except Exception:
        return []
    return out[-5:]
