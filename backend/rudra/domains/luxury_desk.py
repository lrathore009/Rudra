"""Luxury market desk — snapshots, alerts, library integration."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.data.service import AgentDataService
from rudra.agents.types import AgentType
from rudra.domains.models import LuxuryAlert, LuxuryIntelSnapshot
from rudra.knowledge.luxury import LuxuryCategory, LuxuryIntelligenceService
from rudra.research.reports import ResearchReportService


class LuxuryDeskService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def brief_with_library(
        self,
        subject: str,
        category: LuxuryCategory,
        *,
        depth: str = "standard",
    ) -> dict[str, Any]:
        library = ResearchReportService(self.session, self.user_id)
        cached = await library.find_cached(f"luxury {subject}", min_confidence=0.75)
        if cached and "luxury" in (cached.topic_tags or []):
            return {
                "briefing": cached.content,
                "from_library": True,
                "report_id": str(cached.id),
                "exclusivity_score": 0.8,
                "investment_relevance": 0.5,
            }

        intel_svc = LuxuryIntelligenceService()
        intel = await intel_svc.research(subject, category, depth=depth)
        snapshot = LuxuryIntelSnapshot(
            user_id=self.user_id,
            subject=subject,
            category=category.value,
            briefing=intel.briefing,
            exclusivity_score=intel.exclusivity_score,
            investment_relevance=intel.investment_relevance,
            metadata_={"sources": intel.sources[:5]},
        )
        self.session.add(snapshot)
        await self.session.flush()

        report = await library.save(
            title=f"Luxury: {subject[:80]}",
            query=subject,
            content=intel.briefing,
            confidence_score=0.85,
            topic_tags=["luxury", category.value],
            agent_id="luxury_analyst",
        )
        return {
            "briefing": intel.briefing,
            "from_library": False,
            "snapshot_id": str(snapshot.id),
            "report_id": str(report.id),
            "exclusivity_score": intel.exclusivity_score,
            "investment_relevance": intel.investment_relevance,
        }

    async def list_snapshots(self, *, limit: int = 10) -> list[LuxuryIntelSnapshot]:
        result = await self.session.execute(
            select(LuxuryIntelSnapshot)
            .where(LuxuryIntelSnapshot.user_id == self.user_id)
            .order_by(LuxuryIntelSnapshot.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def set_alert(
        self,
        watchlist_title: str,
        *,
        alert_type: str = "price_change",
        threshold: float | None = None,
    ) -> LuxuryAlert:
        row = LuxuryAlert(
            user_id=self.user_id,
            watchlist_title=watchlist_title,
            alert_type=alert_type,
            threshold=threshold,
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_alerts(self) -> list[LuxuryAlert]:
        result = await self.session.execute(
            select(LuxuryAlert).where(
                LuxuryAlert.user_id == self.user_id,
                LuxuryAlert.enabled == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())

    async def desk_trends(self) -> dict[str, Any]:
        snapshots = await self.list_snapshots(limit=50)
        data = AgentDataService(self.session, self.user_id)
        watchlist = await data.list_artifacts(AgentType.LUXURY_ANALYST, artifact_type="watchlist", limit=20)
        if not snapshots:
            return {"count": 0, "avg_exclusivity": 0, "watchlist_count": len(watchlist)}
        avg = sum(s.exclusivity_score for s in snapshots) / len(snapshots)
        return {
            "count": len(snapshots),
            "avg_exclusivity": round(avg, 3),
            "watchlist_count": len(watchlist),
            "recent": [{"subject": s.subject, "category": s.category} for s in snapshots[:5]],
        }

    async def monitor_watchlist(self) -> list[str]:
        triggered = []
        now = datetime.now(timezone.utc).isoformat()
        for alert in await self.list_alerts():
            alert.last_triggered = now
            triggered.append(alert.watchlist_title)
        await self.session.flush()
        return triggered

    async def export_for_federation(self, *, limit: int = 30) -> list[dict[str, Any]]:
        snaps = await self.list_snapshots(limit=limit)
        return [
            {
                "type": "luxury_snapshot",
                "subject": s.subject,
                "category": s.category,
                "briefing": s.briefing[:2000],
            }
            for s in snaps
        ]
