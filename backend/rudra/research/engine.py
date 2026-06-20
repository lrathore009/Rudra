"""Research engine — multi-source intelligence gathering with credibility scoring."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

from rudra.brain.orchestrator import Brain, Message
from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)


class SourceType(str, Enum):
    WEB = "web"
    NEWS = "news"
    ACADEMIC = "academic"
    KNOWLEDGE_BASE = "knowledge_base"
    USER_MEMORY = "user_memory"


@dataclass
class ResearchSource:
    url: str
    title: str
    snippet: str
    source_type: SourceType
    credibility_score: float = 0.5
    published_at: str | None = None


@dataclass
class ResearchResult:
    query: str
    summary: str
    findings: list[str]
    sources: list[ResearchSource]
    confidence_score: float
    citations: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class CredibilityEvaluator:
    """Score source reliability based on domain heuristics."""

    TRUSTED_DOMAINS = {
        "reuters.com": 0.95,
        "bloomberg.com": 0.95,
        "ft.com": 0.9,
        "wsj.com": 0.9,
        "nature.com": 0.98,
        "arxiv.org": 0.85,
        "sec.gov": 0.98,
        "who.int": 0.95,
    }

    @classmethod
    def score(cls, url: str, source_type: SourceType) -> float:
        base_scores = {
            SourceType.ACADEMIC: 0.85,
            SourceType.NEWS: 0.7,
            SourceType.WEB: 0.5,
            SourceType.KNOWLEDGE_BASE: 0.9,
            SourceType.USER_MEMORY: 0.95,
        }
        score = base_scores.get(source_type, 0.5)

        for domain, domain_score in cls.TRUSTED_DOMAINS.items():
            if domain in url.lower():
                return domain_score

        return score


class WebSearchProvider:
    """Free-first web search: DuckDuckGo (no key) → Tavily only if a key exists."""

    async def search(self, query: str, max_results: int = 10) -> list[ResearchSource]:
        results = await self._duckduckgo(query, max_results)
        if results:
            return results
        return await self._tavily(query, max_results)

    async def _duckduckgo(self, query: str, max_results: int) -> list[ResearchSource]:
        import asyncio

        def _run() -> list[dict]:
            try:
                from ddgs import DDGS
            except ImportError:  # pragma: no cover
                from duckduckgo_search import DDGS  # type: ignore
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results))

        try:
            raw = await asyncio.to_thread(_run)
        except Exception as e:  # noqa: BLE001
            logger.warning("duckduckgo_failed", error=str(e)[:120])
            return []

        sources: list[ResearchSource] = []
        for item in raw:
            url = item.get("href") or item.get("url") or ""
            sources.append(
                ResearchSource(
                    url=url,
                    title=item.get("title", ""),
                    snippet=item.get("body", ""),
                    source_type=SourceType.WEB,
                    credibility_score=CredibilityEvaluator.score(url, SourceType.WEB),
                )
            )
        return sources

    async def _tavily(self, query: str, max_results: int) -> list[ResearchSource]:
        settings = get_settings()
        if not settings.tavily_api_key:
            return []
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.tavily_api_key.get_secret_value(),
                    "query": query,
                    "max_results": max_results,
                    "include_answer": False,
                },
            )
            if response.status_code != 200:
                return []
            data = response.json()
            sources = []
            for item in data.get("results", []):
                url = item.get("url", "")
                sources.append(
                    ResearchSource(
                        url=url,
                        title=item.get("title", ""),
                        snippet=item.get("content", ""),
                        source_type=SourceType.WEB,
                        credibility_score=CredibilityEvaluator.score(url, SourceType.WEB),
                    )
                )
            return sources


class WikipediaProvider:
    """Free encyclopedic source via the public MediaWiki API (no key)."""

    async def search(self, query: str, max_results: int = 3) -> list[ResearchSource]:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "list": "search",
                        "srsearch": query,
                        "srlimit": max_results,
                        "format": "json",
                    },
                    headers={"User-Agent": "Rudra/0.1 (personal-intelligence-os)"},
                )
                resp.raise_for_status()
                hits = resp.json().get("query", {}).get("search", [])
        except Exception as e:  # noqa: BLE001
            logger.warning("wikipedia_failed", error=str(e)[:120])
            return []

        import re

        sources: list[ResearchSource] = []
        for h in hits:
            title = h.get("title", "")
            snippet = re.sub(r"<[^>]+>", "", h.get("snippet", ""))
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            sources.append(
                ResearchSource(
                    url=url,
                    title=title,
                    snippet=snippet,
                    source_type=SourceType.ACADEMIC,
                    credibility_score=0.8,
                )
            )
        return sources


class ResearchEngine:
    """Orchestrates multi-source research with synthesis and confidence scoring."""

    def __init__(self, brain: Brain | None = None):
        self.brain = brain or Brain()
        self.web_search = WebSearchProvider()
        self.wikipedia = WikipediaProvider()

    async def research(
        self,
        query: str,
        *,
        sources: list[SourceType] | None = None,
        max_sources: int = 10,
        user_memories: list[dict[str, Any]] | None = None,
        session=None,
        user_id: str | None = None,
    ) -> ResearchResult:
        sources = sources or [SourceType.WEB, SourceType.KNOWLEDGE_BASE]
        all_sources: list[ResearchSource] = []

        if SourceType.WEB in sources:
            web_results = await self.web_search.search(query, max_results=max_sources)
            all_sources.extend(web_results)

        if SourceType.WEB in sources or SourceType.ACADEMIC in sources:
            wiki_results = await self.wikipedia.search(query, max_results=3)
            all_sources.extend(wiki_results)

        if session and user_id:
            from rudra.research.connectors import (
                arxiv_search,
                document_brain_search,
                edgar_search,
                licensed_feed_search,
                rss_research_search,
            )

            all_sources.extend(await arxiv_search(query, max_results=3))
            all_sources.extend(await edgar_search(query, max_results=3))
            all_sources.extend(await rss_research_search(query, max_results=3))
            all_sources.extend(await licensed_feed_search(query, max_results=2))
            all_sources.extend(await document_brain_search(session, user_id, query, limit=4))

        if SourceType.USER_MEMORY in sources and user_memories:
            for mem in user_memories:
                all_sources.append(
                    ResearchSource(
                        url=f"memory://{mem.get('id', 'unknown')}",
                        title=mem.get("title", "User Memory"),
                        snippet=mem.get("content", "")[:500],
                        source_type=SourceType.USER_MEMORY,
                        credibility_score=0.95,
                    )
                )

        if not all_sources:
            synthesis = await self._synthesize_from_model(query, [])
            return ResearchResult(
                query=query,
                summary=synthesis["summary"],
                findings=synthesis["findings"],
                sources=[],
                confidence_score=0.3,
                citations=[],
            )

        synthesis = await self._synthesize_from_model(query, all_sources)
        avg_credibility = sum(s.credibility_score for s in all_sources) / len(all_sources)
        confidence = min(0.95, avg_credibility * (0.5 + 0.05 * len(all_sources)))

        citations = [
            {"title": s.title, "url": s.url, "credibility": str(s.credibility_score)}
            for s in all_sources
        ]

        logger.info(
            "research_complete",
            query=query[:80],
            sources=len(all_sources),
            confidence=confidence,
        )

        return ResearchResult(
            query=query,
            summary=synthesis["summary"],
            findings=synthesis["findings"],
            sources=all_sources,
            confidence_score=confidence,
            citations=citations,
        )

    async def _synthesize_from_model(
        self, query: str, sources: list[ResearchSource]
    ) -> dict[str, Any]:
        source_block = "\n\n".join(
            f"[{i + 1}] {s.title} (credibility: {s.credibility_score})\n{s.snippet}"
            for i, s in enumerate(sources)
        ) or "No external sources available."

        prompt = f"""Research Query: {query}

Sources:
{source_block}

Provide a structured research synthesis:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points)
3. Confidence Assessment (note any gaps or uncertainties)

Be precise. Cite source numbers [1], [2] when referencing specific sources."""

        result = await self.brain.think(
            [Message(role="user", content=prompt)],
            system="You are an institutional research analyst. Synthesize information with rigor.",
            model_tier="reasoning",
        )

        lines = result.content.split("\n")
        findings = [ln.strip("- •") for ln in lines if ln.strip().startswith(("-", "•", "*"))]

        return {
            "summary": result.content,
            "findings": findings[:10] if findings else [result.content[:500]],
        }
