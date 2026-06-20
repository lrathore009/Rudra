"""Unified research pipeline — library-first, then engine."""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from rudra.core.config import get_settings
from rudra.jarvis.events import EventType, get_event_bus
from rudra.jarvis.telemetry import log_inference_telemetry
from rudra.research.engine import ResearchEngine, ResearchResult, SourceType
from rudra.research.reports import ResearchReportService


async def research_with_library(
    session: AsyncSession,
    user_id: str,
    query: str,
    *,
    sources: list[SourceType] | None = None,
    max_sources: int = 10,
    user_memories: list[dict[str, Any]] | None = None,
    force_refresh: bool = False,
) -> tuple[ResearchResult, ResearchReportService, Any | None]:
    """Search library first; run engine if cache miss or force_refresh."""
    library = ResearchReportService(session, user_id)
    settings = get_settings()
    get_event_bus().publish(EventType.RESEARCH_STARTED, {"query": query[:120], "user_id": user_id})

    if not force_refresh:
        cached = await library.find_cached(query, min_confidence=settings.research_min_confidence_cache)
        if cached:
            result = ResearchResult(
                query=query,
                summary=cached.content,
                findings=cached.metadata_.get("findings", []) if cached.metadata_ else [],
                sources=[],
                confidence_score=cached.confidence_score,
                citations=cached.citations or [],
                metadata={"from_library": True, "report_id": str(cached.id)},
            )
            get_event_bus().publish(
                EventType.RESEARCH_COMPLETED,
                {"query": query[:120], "cached": True, "report_id": str(cached.id)},
            )
            return result, library, cached

    t0 = time.perf_counter()
    engine = ResearchEngine()
    result = await engine.research(
        query,
        sources=sources,
        max_sources=max_sources,
        user_memories=user_memories,
        session=session,
        user_id=user_id,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    telem = log_inference_telemetry(
        model="multi-source",
        provider="research_engine",
        latency_ms=latency_ms,
        prompt_tokens=len(query.split()) * 4,
        completion_tokens=len(result.summary.split()) * 2,
        route="cloud" if result.confidence_score > 0.7 else "local",
        summary=query[:80],
    )
    from dataclasses import asdict

    report = await library.save_from_engine_result(result, telemetry=asdict(telem))
    get_event_bus().publish(
        EventType.RESEARCH_COMPLETED,
        {
            "query": query[:120],
            "cached": False,
            "report_id": str(report.id),
            "confidence": result.confidence_score,
        },
    )
    return result, library, report
