"""Unified retrieval — fuse memories, documents, research, and graph."""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from rudra.domains.models import RetrievalTrace
from rudra.graph.service import GraphService
from rudra.memory.hybrid import hybrid_search
from rudra.memory.service import MemoryService
from rudra.research.hybrid import hybrid_search_reports
from rudra.research.reports import ResearchReportService


class LibrarianRetrievalService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def unified_search(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        """Four-source RRF-style merge of memories, documents, research, graph."""
        hits: list[tuple[str, dict[str, Any], float]] = []

        mem_svc = MemoryService(self.session, self.user_id)
        for rank, (mem, score) in enumerate(await hybrid_search(mem_svc, query, limit=limit)):
            hits.append(
                (
                    "memory",
                    {
                        "type": "memory",
                        "id": str(mem.id),
                        "title": mem.title,
                        "snippet": mem.content[:240],
                    },
                    1 / (60 + rank) + score * 0.1,
                )
            )

        try:
            from rudra.documents.service import DocumentService

            doc_svc = DocumentService(self.session, self.user_id)
            for rank, (chunk, doc, sim) in enumerate(await doc_svc.search(query, limit=limit)):
                hits.append(
                    (
                        f"doc:{chunk.id}",
                        {
                            "type": "document",
                            "id": str(doc.id),
                            "title": doc.filename,
                            "snippet": chunk.content[:240],
                        },
                        1 / (60 + rank) + sim * 0.15,
                    )
                )
        except Exception:
            pass

        report_svc = ResearchReportService(self.session, self.user_id)
        for rank, (report, score) in enumerate(await hybrid_search_reports(report_svc, query, limit=limit)):
            hits.append(
                (
                    f"report:{report.id}",
                    {
                        "type": "research_report",
                        "id": str(report.id),
                        "title": report.title,
                        "snippet": report.content[:240],
                    },
                    1 / (60 + rank) + score * 0.12,
                )
            )

        graph = GraphService(self.session, self.user_id)
        entities = await graph.list_entities(query=query[:80], limit=limit)
        for rank, ent in enumerate(entities):
            hits.append(
                (
                    f"entity:{ent.id}",
                    {
                        "type": "entity",
                        "id": str(ent.id),
                        "title": ent.name,
                        "snippet": (ent.description or ent.entity_type)[:240],
                    },
                    1 / (60 + rank),
                )
            )

        hits.sort(key=lambda x: -x[2])
        seen: set[str] = set()
        merged: list[dict[str, Any]] = []
        for key, item, score in hits:
            if key in seen:
                continue
            seen.add(key)
            item["score"] = round(score, 4)
            merged.append(item)
            if len(merged) >= limit:
                break
        return merged

    async def answer(self, query: str, *, limit: int = 8) -> dict[str, Any]:
        t0 = time.perf_counter()
        sources = await self.unified_search(query, limit=limit)
        if not sources:
            answer = "No relevant knowledge found across memories, documents, research, or graph."
        else:
            blocks = [f"Query: {query}", "", "Sources:"]
            for s in sources:
                blocks.append(f"- [{s['type']}] {s['title']}: {s['snippet']}")
            blocks.append("")
            blocks.append(
                "Synthesis: Cross-reference the sources above. Cite specific memories, documents, "
                "research reports, and entities when answering."
            )
            answer = "\n".join(blocks)

        latency = int((time.perf_counter() - t0) * 1000)
        trace = RetrievalTrace(
            user_id=self.user_id,
            query=query,
            answer_preview=answer[:2000],
            sources=sources,
            latency_ms=latency,
        )
        self.session.add(trace)
        await self.session.flush()
        return {"answer": answer, "sources": sources, "trace_id": str(trace.id), "latency_ms": latency}

    async def recent_traces(self, *, limit: int = 10) -> list[RetrievalTrace]:
        from sqlalchemy import select

        result = await self.session.execute(
            select(RetrievalTrace)
            .where(RetrievalTrace.user_id == self.user_id)
            .order_by(RetrievalTrace.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def export_for_federation(self, *, limit: int = 50) -> list[dict[str, Any]]:
        traces = await self.recent_traces(limit=limit)
        return [
            {
                "type": "retrieval_trace",
                "query": t.query,
                "answer_preview": t.answer_preview,
                "sources": t.sources,
            }
            for t in traces
        ]
