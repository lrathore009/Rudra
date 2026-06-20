"""Research report library — Phase 2 persistence, hybrid search, watchlist, pipeline."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.memory.models.memory import ResearchReport
from rudra.research.models import ResearchJob, ResearchWatchlist


def _query_hash(query: str) -> str:
    return hashlib.sha256(query.strip().lower().encode()).hexdigest()[:32]


class ResearchReportService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def save(
        self,
        *,
        title: str,
        query: str,
        content: str,
        confidence_score: float = 0.8,
        citations: list[dict[str, Any]] | None = None,
        sources: list[dict[str, Any]] | None = None,
        agent_id: str = "research_analyst",
        topic_tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        supersede_days: int = 7,
    ) -> ResearchReport:
        qh = _query_hash(query)
        existing = await self._find_recent_by_hash(qh, days=supersede_days)
        if existing:
            existing.status = "superseded"
            parent_id = existing.id
        else:
            parent_id = None

        embedding = await self._embed(f"{title}\n\n{query}\n\n{content[:2000]}")
        report = ResearchReport(
            user_id=self.user_id,
            title=title,
            query=query,
            content=content,
            confidence_score=confidence_score,
            citations=citations,
            sources=sources,
            agent_id=agent_id,
            embedding=embedding,
            topic_tags=topic_tags,
            parent_id=parent_id,
            metadata_=metadata,
            query_hash=qh,
            status="completed",
        )
        self.session.add(report)
        await self.session.flush()
        return report

    async def save_from_engine_result(
        self,
        result: Any,
        *,
        title: str | None = None,
        telemetry: dict | None = None,
    ) -> ResearchReport:
        from rudra.research.connectors import extract_topic_tags

        report = await self.save(
            title=title or f"Research: {result.query[:80]}",
            query=result.query,
            content=result.summary,
            confidence_score=result.confidence_score,
            citations=result.citations,
            sources=[
                {"title": s.title, "url": s.url, "credibility": s.credibility_score}
                for s in result.sources
            ],
            topic_tags=extract_topic_tags(result.query, result.summary),
            metadata={"findings": result.findings, "source_count": len(result.sources)},
        )
        job = ResearchJob(
            user_id=self.user_id,
            query=result.query,
            status="completed",
            report_id=str(report.id),
            source_count=len(result.sources),
            confidence_score=result.confidence_score,
            telemetry_=telemetry,
        )
        self.session.add(job)
        await self.session.flush()
        await self._link_graph_entities(result.query, result.summary)
        return report

    async def get(self, report_id: uuid.UUID) -> ResearchReport | None:
        result = await self.session.execute(
            select(ResearchReport).where(
                ResearchReport.id == report_id,
                ResearchReport.user_id == self.user_id,
            )
        )
        return result.scalar_one_or_none()

    async def search(self, query: str, *, limit: int = 10) -> list[ResearchReport]:
        like = f"%{query.lower()}%"
        result = await self.session.execute(
            select(ResearchReport)
            .where(
                ResearchReport.user_id == self.user_id,
                ResearchReport.status == "completed",
                or_(
                    func.lower(ResearchReport.title).like(like),
                    func.lower(ResearchReport.query).like(like),
                    func.lower(ResearchReport.content).like(like),
                ),
            )
            .order_by(ResearchReport.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_semantic(
        self, query: str, *, limit: int = 10, min_sim: float = 0.35
    ) -> list[tuple[ResearchReport, float]]:
        from rudra.brain.embeddings import embed_text

        vec = await embed_text(query)
        if not vec:
            return []
        sql = text("""
            SELECT id, 1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM research_reports
            WHERE user_id = :user_id
              AND status = 'completed'
              AND embedding IS NOT NULL
              AND 1 - (embedding <=> CAST(:embedding AS vector)) >= :min_sim
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)
        result = await self.session.execute(
            sql,
            {
                "embedding": str(vec),
                "user_id": self.user_id,
                "min_sim": min_sim,
                "limit": limit,
            },
        )
        rows = result.fetchall()
        if not rows:
            return []
        ids = [r[0] for r in rows]
        sims = {r[0]: float(r[1]) for r in rows}
        reports = await self.session.execute(
            select(ResearchReport).where(ResearchReport.id.in_(ids))
        )
        out = [(r, sims[r.id]) for r in reports.scalars().all() if r.id in sims]
        out.sort(key=lambda x: -x[1])
        return out

    async def find_cached(self, query: str, *, min_confidence: float = 0.75) -> ResearchReport | None:
        hits = await self.search(query, limit=3)
        for h in hits:
            if h.confidence_score >= min_confidence:
                return h
        semantic = await self.search_semantic(query, limit=1, min_sim=0.5)
        if semantic and semantic[0][0].confidence_score >= min_confidence:
            return semantic[0][0]
        return None

    async def list_recent(self, *, limit: int = 10) -> list[ResearchReport]:
        result = await self.session.execute(
            select(ResearchReport)
            .where(
                ResearchReport.user_id == self.user_id,
                ResearchReport.status == "completed",
            )
            .order_by(ResearchReport.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def trends(self) -> dict[str, Any]:
        result = await self.session.execute(
            select(ResearchReport)
            .where(
                ResearchReport.user_id == self.user_id,
                ResearchReport.status == "completed",
            )
            .order_by(ResearchReport.created_at.desc())
            .limit(100)
        )
        reports = list(result.scalars().all())
        if not reports:
            return {"count": 0, "avg_confidence": 0, "weekly": [], "stale_count": 0}
        avg = sum(r.confidence_score for r in reports) / len(reports)
        stale = sum(
            1
            for r in reports
            if r.created_at and (datetime.now(r.created_at.tzinfo) - r.created_at).days > 30
        )
        weekly: dict[str, list[float]] = {}
        for r in reports:
            key = r.created_at.strftime("%Y-%W") if r.created_at else "unknown"
            weekly.setdefault(key, []).append(r.confidence_score)
        trend = [
            {"week": k, "avg_confidence": round(sum(v) / len(v), 3), "count": len(v)}
            for k, v in sorted(weekly.items())[-8:]
        ]
        return {
            "count": len(reports),
            "avg_confidence": round(avg, 3),
            "weekly": trend,
            "stale_count": stale,
        }

    async def list_watchlist(self) -> list[ResearchWatchlist]:
        result = await self.session.execute(
            select(ResearchWatchlist)
            .where(ResearchWatchlist.user_id == self.user_id, ResearchWatchlist.enabled == True)  # noqa: E712
            .order_by(ResearchWatchlist.topic)
        )
        return list(result.scalars().all())

    async def add_watchlist(self, topic: str, query_template: str, *, ttl_days: int = 30) -> ResearchWatchlist:
        row = ResearchWatchlist(
            user_id=self.user_id,
            topic=topic,
            query_template=query_template,
            ttl_days=ttl_days,
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def export_for_federation(self, *, limit: int = 100) -> list[dict[str, Any]]:
        reports = await self.list_recent(limit=limit)
        return [
            {
                "title": r.title,
                "query": r.query,
                "content": r.content[:4000],
                "confidence_score": r.confidence_score,
                "citations": r.citations,
                "sources": r.sources,
                "topic_tags": r.topic_tags,
            }
            for r in reports
        ]

    async def import_from_federation(self, items: list[dict[str, Any]]) -> int:
        count = 0
        for item in items[:50]:
            await self.save(
                title=str(item.get("title", "Synced report"))[:512],
                query=str(item.get("query", "")),
                content=str(item.get("content", "")),
                confidence_score=float(item.get("confidence_score", 0.7)),
                citations=item.get("citations"),
                sources=item.get("sources"),
                agent_id="federation",
                topic_tags=item.get("topic_tags"),
            )
            count += 1
        return count

    async def _find_recent_by_hash(self, qh: str, *, days: int) -> ResearchReport | None:
        result = await self.session.execute(
            select(ResearchReport)
            .where(
                ResearchReport.user_id == self.user_id,
                ResearchReport.query_hash == qh,
                ResearchReport.status == "completed",
            )
            .order_by(ResearchReport.created_at.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        if not row or not row.created_at:
            return None
        if (datetime.now(row.created_at.tzinfo) - row.created_at).days <= days:
            return row
        return None

    async def _embed(self, text: str) -> list[float] | None:
        from rudra.brain.embeddings import embed_text

        try:
            return await embed_text(text)
        except Exception:
            return None

    async def _link_graph_entities(self, query: str, content: str) -> None:
        try:
            from rudra.graph.service import GraphService

            gs = GraphService(self.session, self.user_id)
            await gs.extract_from_text(f"{query}\n{content[:1500]}", use_llm=False)
        except Exception:
            pass
