"""#13 — Hybrid memory retrieval: BM25-ish keyword + vector RRF fusion."""

from __future__ import annotations

from sqlalchemy import func, or_, select

from rudra.memory.models.memory import Memory, MemoryTag
from rudra.memory.service import MemoryService


async def hybrid_search(
    svc: MemoryService,
    query: str,
    *,
    limit: int = 10,
    tags: list[str] | None = None,
) -> list[tuple[Memory, float]]:
    """Reciprocal rank fusion of keyword and semantic hits."""
    keyword_hits = await _keyword_search(svc, query, limit=limit * 2, tags=tags)
    semantic_hits = await svc.search_by_text(query, limit=limit * 2)
    scores: dict = {}
    for rank, (mem, _) in enumerate(keyword_hits):
        scores[mem.id] = scores.get(mem.id, 0) + 1 / (60 + rank)
    for rank, (mem, sim) in enumerate(semantic_hits):
        scores[mem.id] = scores.get(mem.id, 0) + 1 / (60 + rank) + sim * 0.1
    merged: list[tuple[Memory, float]] = []
    seen = {m.id: m for m, _ in keyword_hits}
    seen.update({m.id: m for m, _ in semantic_hits})
    for mid, score in sorted(scores.items(), key=lambda x: -x[1])[:limit]:
        if mid in seen:
            merged.append((seen[mid], score))
    return merged


async def _keyword_search(
    svc: MemoryService,
    query: str,
    *,
    limit: int,
    tags: list[str] | None,
) -> list[tuple[Memory, float]]:
    like = f"%{query.lower()}%"
    stmt = (
        select(Memory)
        .where(
            Memory.user_id == svc.user_id,
            Memory.is_deleted == False,  # noqa: E712
            or_(
                func.lower(Memory.title).like(like),
                func.lower(Memory.content).like(like),
            ),
        )
        .order_by(Memory.importance.desc())
        .limit(limit)
    )
    if tags:
        stmt = stmt.join(MemoryTag, MemoryTag.memory_id == Memory.id).where(MemoryTag.tag.in_(tags))
    result = await svc.session.execute(stmt)
    memories = list(result.scalars().unique().all())
    return [(m, 0.5) for m in memories]
