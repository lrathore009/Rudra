"""Memory service — CRUD, search, and knowledge graph operations."""

import uuid
from typing import Any

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.memory.models.memory import Memory, MemoryLink, MemoryTag, MemoryType, Preference


class MemoryService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def create(
        self,
        memory_type: MemoryType,
        title: str,
        content: str,
        *,
        summary: str | None = None,
        embedding: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
        importance: float = 0.5,
        source: str | None = None,
        tags: list[str] | None = None,
    ) -> Memory:
        # Auto-generate a free embedding when none is supplied (graceful if unavailable).
        if embedding is None:
            from rudra.brain.embeddings import embed_text

            try:
                embedding = await embed_text(f"{title}\n\n{content}")
            except Exception:  # noqa: BLE001
                embedding = None

        memory = Memory(
            user_id=self.user_id,
            memory_type=memory_type.value,
            title=title,
            content=content,
            summary=summary,
            embedding=embedding,
            metadata_=metadata,
            importance=importance,
            source=source,
        )
        self.session.add(memory)
        await self.session.flush()

        if tags:
            for tag in tags:
                self.session.add(MemoryTag(memory_id=memory.id, tag=tag))

        return memory

    async def get(self, memory_id: uuid.UUID) -> Memory | None:
        result = await self.session.execute(
            select(Memory).where(
                Memory.id == memory_id,
                Memory.user_id == self.user_id,
                Memory.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def search_semantic(
        self,
        query_embedding: list[float],
        *,
        memory_type: MemoryType | None = None,
        limit: int = 10,
        min_similarity: float = 0.7,
    ) -> list[tuple[Memory, float]]:
        type_filter = ""
        params: dict[str, Any] = {
            "user_id": self.user_id,
            "embedding": str(query_embedding),
            "limit": limit,
            "min_sim": min_similarity,
        }
        if memory_type:
            type_filter = "AND memory_type = :memory_type"
            params["memory_type"] = memory_type.value

        # NOTE: use CAST(:embedding AS vector) rather than :embedding::vector.
        # SQLAlchemy's text() will not treat a bind param immediately followed by
        # "::" as a parameter, which silently breaks the query.
        sql = text(f"""
            SELECT id, 1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM memories
            WHERE user_id = :user_id
              AND is_deleted = false
              AND embedding IS NOT NULL
              {type_filter}
              AND 1 - (embedding <=> CAST(:embedding AS vector)) >= :min_sim
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)
        result = await self.session.execute(sql, params)
        rows = result.fetchall()

        memories = []
        for row in rows:
            mem = await self.get(row.id)
            if mem:
                memories.append((mem, row.similarity))
        return memories

    async def search_by_text(
        self,
        query: str,
        *,
        memory_type: MemoryType | None = None,
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> list[tuple[Memory, float]]:
        """Embed the query for free, then run semantic vector search."""
        from rudra.brain.embeddings import embed_text

        vec = await embed_text(query)
        if vec is None:
            # No embedding backend available — fall back to recent memories.
            recent = await self.list_recent(memory_type=memory_type, limit=limit)
            return [(m, 0.0) for m in recent]
        return await self.search_semantic(
            vec, memory_type=memory_type, limit=limit, min_similarity=min_similarity
        )

    async def link_memories(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        relation_type: str,
        weight: float = 1.0,
    ) -> MemoryLink:
        link = MemoryLink(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
        )
        self.session.add(link)
        await self.session.flush()
        return link

    async def delete(self, memory_id: uuid.UUID, *, hard: bool = False) -> bool:
        memory = await self.get(memory_id)
        if not memory:
            return False

        if hard:
            await self.session.delete(memory)
        else:
            await self.session.execute(
                update(Memory)
                .where(Memory.id == memory_id)
                .values(is_deleted=True)
            )
        return True

    async def list_recent(
        self,
        *,
        memory_type: MemoryType | None = None,
        limit: int = 20,
    ) -> list[Memory]:
        query = (
            select(Memory)
            .where(Memory.user_id == self.user_id, Memory.is_deleted == False)  # noqa: E712
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        if memory_type:
            query = query.where(Memory.memory_type == memory_type.value)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_by_tags(self, tags: list[str], *, limit: int = 10) -> list[Memory]:
        if not tags:
            return []
        result = await self.session.execute(
            select(Memory)
            .join(MemoryTag, MemoryTag.memory_id == Memory.id)
            .where(
                Memory.user_id == self.user_id,
                Memory.is_deleted == False,  # noqa: E712
                MemoryTag.tag.in_(tags),
            )
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().unique().all())

    async def list_preferences(
        self,
        *,
        category: str | None = None,
        limit: int = 50,
    ) -> list[Preference]:
        query = select(Preference).where(Preference.user_id == self.user_id).limit(limit)
        if category:
            query = query.where(Preference.category == category)
        result = await self.session.execute(query)
        return list(result.scalars().all())
