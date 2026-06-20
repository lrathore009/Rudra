"""Research source connectors — arXiv, SEC EDGAR, documents, licensed feeds."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import httpx

from rudra.core.config import get_settings
from rudra.core.logging import get_logger
from rudra.research.engine import ResearchSource, SourceType

logger = get_logger(__name__)


async def arxiv_search(query: str, *, max_results: int = 5) -> list[ResearchSource]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                "http://export.arxiv.org/api/query",
                params={"search_query": f"all:{query}", "max_results": max_results},
            )
            r.raise_for_status()
            root = ET.fromstring(r.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            out: list[ResearchSource] = []
            for entry in root.findall("atom:entry", ns)[:max_results]:
                title = (entry.find("atom:title", ns).text or "").strip().replace("\n", " ")
                summary = (entry.find("atom:summary", ns).text or "")[:400]
                link = next(
                    (l.attrib.get("href") for l in entry.findall("atom:link", ns) if l.attrib.get("type") == "text/html"),
                    "",
                )
                out.append(
                    ResearchSource(
                        url=link or "https://arxiv.org",
                        title=title,
                        snippet=summary,
                        source_type=SourceType.ACADEMIC,
                        credibility_score=0.88,
                    )
                )
            return out
    except Exception as e:  # noqa: BLE001
        logger.warning("arxiv_search_failed", error=str(e)[:120])
        return []


async def edgar_search(query: str, *, max_results: int = 5) -> list[ResearchSource]:
    """SEC full-text search (free, no key)."""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(
                "https://efts.sec.gov/LATEST/search-index",
                params={"q": query, "dateRange": "custom", "startdt": "2024-01-01", "forms": "10-K,10-Q,8-K"},
                headers={"User-Agent": "Rudra/0.1 research@local"},
            )
            if r.status_code != 200:
                return []
            data = r.json()
            hits = data.get("hits", {}).get("hits", [])[:max_results]
            out: list[ResearchSource] = []
            for hit in hits:
                src = hit.get("_source", {})
                out.append(
                    ResearchSource(
                        url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={src.get('ciks', [''])[0]}",
                        title=src.get("display_names", [query])[0] if src.get("display_names") else query,
                        snippet=(src.get("file_description") or src.get("form") or "")[:300],
                        source_type=SourceType.ACADEMIC,
                        credibility_score=0.98,
                    )
                )
            return out
    except Exception as e:  # noqa: BLE001
        logger.warning("edgar_search_failed", error=str(e)[:120])
        return []


async def document_brain_search(session, user_id: str, query: str, *, limit: int = 5) -> list[ResearchSource]:
    try:
        from rudra.documents.service import DocumentService

        svc = DocumentService(session, user_id)
        hits = await svc.search(query, limit=limit)
        return [
            ResearchSource(
                url=f"document://{doc.id}",
                title=doc.filename,
                snippet=chunk.content[:400],
                source_type=SourceType.KNOWLEDGE_BASE,
                credibility_score=0.92,
            )
            for chunk, doc, _ in hits
        ]
    except Exception as e:  # noqa: BLE001
        logger.warning("document_search_failed", error=str(e)[:120])
        return []


async def licensed_feed_search(query: str, *, max_results: int = 5) -> list[ResearchSource]:
    """Bloomberg / FactSet scaffold — returns data when API keys configured."""
    settings = get_settings()
    out: list[ResearchSource] = []
    if settings.bloomberg_api_key:
        out.append(
            ResearchSource(
                url="bloomberg://feed",
                title=f"Bloomberg: {query[:80]}",
                snippet="Licensed Bloomberg feed connected (stub synthesis).",
                source_type=SourceType.NEWS,
                credibility_score=0.95,
            )
        )
    if settings.factset_api_key:
        out.append(
            ResearchSource(
                url="factset://feed",
                title=f"FactSet: {query[:80]}",
                snippet="Licensed FactSet feed connected (stub synthesis).",
                source_type=SourceType.NEWS,
                credibility_score=0.94,
            )
        )
    if settings.chrono24_api_key:
        out.append(
            ResearchSource(
                url="chrono24://feed",
                title=f"Chrono24: {query[:80]}",
                snippet="Licensed watch market feed connected (stub).",
                source_type=SourceType.NEWS,
                credibility_score=0.9,
            )
        )
    if settings.artsy_api_key:
        out.append(
            ResearchSource(
                url="artsy://feed",
                title=f"Artsy: {query[:80]}",
                snippet="Licensed art market feed connected (stub).",
                source_type=SourceType.NEWS,
                credibility_score=0.88,
            )
        )
    return out[:max_results]


async def rss_research_search(query: str, *, max_results: int = 5) -> list[ResearchSource]:
    from rudra.jarvis.connectors.news import NewsConnector

    conn = NewsConnector(None)
    headlines = await conn.headlines("owner", limit=max_results)
    q = query.lower()
    return [
        ResearchSource(
            url=h.url or "",
            title=h.title,
            snippet=h.title,
            source_type=SourceType.NEWS,
            credibility_score=0.75,
        )
        for h in headlines
        if not q or any(w in h.title.lower() for w in q.split()[:4])
    ][:max_results]


def extract_topic_tags(query: str, content: str) -> list[str]:
    tags: list[str] = []
    blob = f"{query} {content}".lower()
    for tag in ("chemsphere", "jobsflix", "rudra", "luxury", "uhni", "ai", "regulatory", "travel"):
        if tag in blob:
            tags.append(tag)
    return tags[:8]
