"""Research and luxury intelligence API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.api.schemas import (
    LuxuryIntelligenceResponse,
    LuxuryResearchRequest,
    ResearchRequest,
    ResearchResponse,
)
from rudra.core.database import get_db
from rudra.knowledge.luxury import LuxuryCategory, LuxuryIntelligenceService
from rudra.memory.models.memory import MemoryType
from rudra.memory.service import MemoryService
from rudra.research.engine import SourceType
from rudra.research.hybrid import hybrid_search_reports
from rudra.research.pipeline import research_with_library
from rudra.research.reports import ResearchReportService
from rudra.security.audit import AuditAction, log_audit

router = APIRouter(tags=["research"])


class WatchlistRequest(BaseModel):
    topic: str
    query_template: str
    ttl_days: int = 30


class LibrarySearchRequest(BaseModel):
    query: str
    limit: int = 10
    hybrid: bool = True


@router.post("/research", response_model=ResearchResponse)
async def conduct_research(
    request: ResearchRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    await log_audit(db, AuditAction.RESEARCH_START, user_id, details={"query": request.query})

    memory_service = MemoryService(db, user_id)
    recent = await memory_service.list_recent(memory_type=MemoryType.RESEARCH, limit=5)
    user_memories = [
        {"id": str(m.id), "title": m.title, "content": m.content} for m in recent
    ]

    source_types = [SourceType(s) for s in request.sources] if request.sources else None
    result, library, report = await research_with_library(
        db,
        user_id,
        request.query,
        sources=source_types,
        max_sources=request.max_sources,
        user_memories=user_memories,
    )

    if report and not result.metadata.get("from_library"):
        await memory_service.create(
            MemoryType.RESEARCH,
            title=f"Research: {request.query[:80]}",
            content=result.summary,
            importance=0.7,
            source="research_engine",
            tags=["research", "auto-generated"],
            metadata={
                "confidence": result.confidence_score,
                "sources": len(result.sources),
                "report_id": str(report.id),
            },
        )

    await log_audit(
        db,
        AuditAction.RESEARCH_COMPLETE,
        user_id,
        details={"confidence": result.confidence_score, "report_id": str(report.id) if report else None},
    )

    return ResearchResponse(
        query=result.query,
        summary=result.summary,
        findings=result.findings,
        confidence_score=result.confidence_score,
        citations=result.citations,
        source_count=len(result.sources),
        report_id=str(report.id) if report else result.metadata.get("report_id"),
        from_library=bool(result.metadata.get("from_library")),
    )


@router.get("/research/library")
async def list_library(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
):
    svc = ResearchReportService(db, user_id)
    reports = await svc.list_recent(limit=limit)
    trends = await svc.trends()
    watchlist = await svc.list_watchlist()
    return {
        "reports": [
            {
                "id": str(r.id),
                "title": r.title,
                "query": r.query[:200],
                "confidence_score": r.confidence_score,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "topic_tags": r.topic_tags or [],
            }
            for r in reports
        ],
        "trends": trends,
        "watchlist": [
            {"id": str(w.id), "topic": w.topic, "query_template": w.query_template, "ttl_days": w.ttl_days}
            for w in watchlist
        ],
    }


@router.get("/research/library/{report_id}")
async def get_report(
    report_id: UUID,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    report = await ResearchReportService(db, user_id).get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": str(report.id),
        "title": report.title,
        "query": report.query,
        "content": report.content,
        "confidence_score": report.confidence_score,
        "citations": report.citations,
        "sources": report.sources,
        "topic_tags": report.topic_tags,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


@router.post("/research/library/search")
async def search_library(
    body: LibrarySearchRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ResearchReportService(db, user_id)
    if body.hybrid:
        hits = await hybrid_search_reports(svc, body.query, limit=body.limit)
        return [
            {
                "id": str(r.id),
                "title": r.title,
                "confidence_score": r.confidence_score,
                "score": round(score, 4),
                "snippet": r.content[:240],
            }
            for r, score in hits
        ]
    reports = await svc.search(body.query, limit=body.limit)
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "confidence_score": r.confidence_score,
            "snippet": r.content[:240],
        }
        for r in reports
    ]


@router.post("/research/watchlist")
async def add_watchlist(
    body: WatchlistRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    row = await ResearchReportService(db, user_id).add_watchlist(
        body.topic, body.query_template, ttl_days=body.ttl_days
    )
    return {"id": str(row.id), "topic": row.topic}


@router.get("/research/trends")
async def research_trends(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await ResearchReportService(db, user_id).trends()


@router.post("/luxury/research", response_model=LuxuryIntelligenceResponse)
async def luxury_research(
    request: LuxuryResearchRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    service = LuxuryIntelligenceService()
    intelligence = await service.research(
        request.subject,
        LuxuryCategory(request.category),
        depth=request.depth,
    )

    library = ResearchReportService(db, user_id)
    await library.save(
        title=f"Luxury: {request.subject[:80]}",
        query=request.subject,
        content=intelligence.briefing,
        confidence_score=0.85,
        citations=[{"title": s, "url": ""} for s in intelligence.sources[:5]],
        agent_id="luxury_analyst",
        topic_tags=["luxury", request.category],
    )

    memory_service = MemoryService(db, user_id)
    await memory_service.create(
        MemoryType.RESEARCH,
        title=f"Luxury: {request.subject[:80]}",
        content=intelligence.briefing,
        importance=0.8,
        source="luxury_intelligence",
        tags=["luxury", request.category],
        metadata={
            "exclusivity_score": intelligence.exclusivity_score,
            "investment_relevance": intelligence.investment_relevance,
        },
    )

    return LuxuryIntelligenceResponse(
        category=intelligence.category.value,
        subject=intelligence.subject,
        briefing=intelligence.briefing,
        key_facts=intelligence.key_facts,
        exclusivity_score=intelligence.exclusivity_score,
        investment_relevance=intelligence.investment_relevance,
        sources=intelligence.sources,
    )


@router.get("/luxury/trends")
async def luxury_trends(user_id: str = Depends(require_auth)):
    service = LuxuryIntelligenceService()
    briefing = await service.trend_briefing()
    return {"briefing": briefing}
