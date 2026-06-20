"""Hybrid retrieval for research reports — keyword + vector RRF."""

from __future__ import annotations

from sqlalchemy import func, or_, select, text

from rudra.memory.models.memory import ResearchReport
from rudra.research.reports import ResearchReportService


async def hybrid_search_reports(
    svc: ResearchReportService,
    query: str,
    *,
    limit: int = 10,
) -> list[tuple[ResearchReport, float]]:
    keyword_hits = await svc.search(query, limit=limit * 2)
    keyword_scored = [(r, 0.5) for r in keyword_hits]
    semantic_hits = await svc.search_semantic(query, limit=limit * 2)
    scores: dict = {}
    for rank, report in enumerate(keyword_hits):
        scores[report.id] = scores.get(report.id, 0) + 1 / (60 + rank)
    for rank, (report, sim) in enumerate(semantic_hits):
        scores[report.id] = scores.get(report.id, 0) + 1 / (60 + rank) + sim * 0.15
    merged: list[tuple[ResearchReport, float]] = []
    seen = {r.id: r for r in keyword_hits}
    seen.update({r.id: r for r, _ in semantic_hits})
    for rid, score in sorted(scores.items(), key=lambda x: -x[1])[:limit]:
        if rid in seen:
            merged.append((seen[rid], score))
    return merged
