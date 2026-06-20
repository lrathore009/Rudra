"""Agent 2 — Research Analyst free sources."""

from __future__ import annotations

import asyncio

from rudra.core.config import Settings
from rudra.jarvis.connectors.agent_free_sources._types import IntelItem
from rudra.jarvis.connectors.free_sources._http import get_json
from rudra.research.connectors import arxiv_search, edgar_search, rss_research_search


async def fetch_research_intel(settings: Settings, query: str, *, limit: int = 8) -> list[IntelItem]:
    q = query or settings.ea_edgar_watch_query or "technology"
    out: list[IntelItem] = []

    async def _arxiv() -> None:
        for s in await arxiv_search(q, max_results=3):
            out.append(IntelItem(s.title, s.snippet, "arxiv", "academic", s.url))

    async def _edgar() -> None:
        for s in await edgar_search(q, max_results=3):
            out.append(IntelItem(s.title, s.snippet, "sec_edgar", "finance", s.url))

    async def _rss() -> None:
        for s in await rss_research_search(q, max_results=3):
            out.append(IntelItem(s.title, s.snippet, "rss", "news", s.url))

    async def _openalex() -> None:
        data = await get_json(
            "https://api.openalex.org/works",
            params={"search": q, "per_page": 3, "sort": "publication_date:desc"},
        )
        if isinstance(data, dict):
            for w in data.get("results", [])[:3]:
                out.append(
                    IntelItem(
                        (w.get("title") or q)[:120],
                        f"OpenAlex · {w.get('publication_year', '')}",
                        "openalex",
                        "academic",
                        w.get("id"),
                    )
                )

    async def _pubmed() -> None:
        search = await get_json(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", "term": q, "retmode": "json", "retmax": 3},
        )
        ids = (search or {}).get("esearchresult", {}).get("idlist", []) if isinstance(search, dict) else []
        if ids:
            summary = await get_json(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
            )
            if isinstance(summary, dict):
                for pid in ids:
                    item = summary.get("result", {}).get(pid, {})
                    out.append(
                        IntelItem(
                            (item.get("title") or "PubMed")[:120],
                            item.get("source", "PubMed")[:120],
                            "pubmed",
                            "academic",
                        )
                    )

    async def _crossref() -> None:
        data = await get_json("https://api.crossref.org/works", params={"query": q, "rows": 3})
        if isinstance(data, dict):
            for item in data.get("message", {}).get("items", [])[:3]:
                title = (item.get("title") or ["Paper"])[0]
                out.append(IntelItem(title[:120], "Crossref DOI record", "crossref", "academic", item.get("URL")))

    async def _doaj() -> None:
        data = await get_json("https://doaj.org/api/search/articles/" + q[:40], params={"pageSize": 3})
        if isinstance(data, dict):
            for r in data.get("results", [])[:3]:
                bib = r.get("bibjson", {})
                out.append(
                    IntelItem(
                        (bib.get("title") or q)[:120],
                        (bib.get("abstract") or "")[:200],
                        "doaj",
                        "academic",
                    )
                )

    await asyncio.gather(_arxiv(), _edgar(), _rss(), _openalex(), _pubmed(), _crossref(), _doaj(), return_exceptions=True)
    return out[:limit]
