"""Knowledge graph service — entities, relationships, memory links."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from rudra.graph.extraction import ExtractedEntity, extract_entities
from rudra.graph.models import (
    Entity,
    EntityAlias,
    EntityType,
    GraphRelationType,
    GraphRelationship,
    MemoryEntityLink,
    ProjectEntityLink,
)
from rudra.graph.seed import SEED_ENTITIES, SEED_RELATIONSHIPS
from rudra.memory.models.memory import Memory


class GraphService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id

    async def list_entities(
        self,
        *,
        query: str | None = None,
        entity_type: str | None = None,
        limit: int = 50,
    ) -> list[Entity]:
        stmt = (
            select(Entity)
            .where(Entity.user_id == self.user_id)
            .options(selectinload(Entity.aliases))
            .order_by(Entity.name)
            .limit(limit)
        )
        if entity_type:
            stmt = stmt.where(Entity.entity_type == entity_type)
        if query:
            like = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Entity.name).like(like),
                    Entity.id.in_(
                        select(EntityAlias.entity_id).where(func.lower(EntityAlias.alias).like(like))
                    ),
                )
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_entity(self, entity_id: uuid.UUID) -> Entity | None:
        result = await self.session.execute(
            select(Entity)
            .where(Entity.id == entity_id, Entity.user_id == self.user_id)
            .options(selectinload(Entity.aliases))
        )
        return result.scalar_one_or_none()

    async def get_or_create_entity(
        self,
        name: str,
        entity_type: str,
        *,
        description: str | None = None,
    ) -> Entity:
        result = await self.session.execute(
            select(Entity).where(
                Entity.user_id == self.user_id,
                func.lower(Entity.name) == name.lower(),
            ).limit(1)
        )
        existing = result.scalars().first()
        if existing:
            return existing
        entity = Entity(
            user_id=self.user_id,
            name=name.strip(),
            entity_type=entity_type,
            description=description,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def create_relationship(
        self,
        source_entity_id: uuid.UUID,
        target_entity_id: uuid.UUID,
        relation_type: str,
        *,
        weight: float = 1.0,
        notes: str | None = None,
    ) -> GraphRelationship:
        rel = GraphRelationship(
            user_id=self.user_id,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relation_type=relation_type,
            weight=weight,
            notes=notes,
        )
        self.session.add(rel)
        await self.session.flush()
        return rel

    async def list_relationships(
        self,
        *,
        entity_id: uuid.UUID | None = None,
        limit: int = 100,
    ) -> list[GraphRelationship]:
        stmt = select(GraphRelationship).where(GraphRelationship.user_id == self.user_id).limit(limit)
        if entity_id:
            stmt = stmt.where(
                or_(
                    GraphRelationship.source_entity_id == entity_id,
                    GraphRelationship.target_entity_id == entity_id,
                )
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_neighbors(self, entity_id: uuid.UUID, *, limit: int = 10) -> list[dict[str, str]]:
        rels = await self.list_relationships(entity_id=entity_id, limit=limit)
        neighbors: list[dict[str, str]] = []
        for rel in rels:
            other_id = (
                rel.target_entity_id
                if rel.source_entity_id == entity_id
                else rel.source_entity_id
            )
            entity = await self.get_entity(other_id)
            if entity:
                neighbors.append(
                    {
                        "id": str(entity.id),
                        "name": entity.name,
                        "type": entity.entity_type,
                        "relation": rel.relation_type,
                    }
                )
        return neighbors

    async def find_entity_by_name(self, name: str) -> Entity | None:
        result = await self.session.execute(
            select(Entity).where(
                Entity.user_id == self.user_id,
                func.lower(Entity.name) == name.lower(),
            ).limit(1)
        )
        return result.scalars().first()

    async def link_memory(
        self,
        memory_id: uuid.UUID,
        entity_id: uuid.UUID,
        *,
        relation_type: str = GraphRelationType.MENTIONS.value,
        confidence: float = 1.0,
    ) -> MemoryEntityLink:
        link = MemoryEntityLink(
            memory_id=memory_id,
            entity_id=entity_id,
            relation_type=relation_type,
            confidence=confidence,
        )
        self.session.add(link)
        await self.session.flush()
        return link

    async def memories_for_entity(self, entity_id: uuid.UUID, *, limit: int = 20) -> list[Memory]:
        result = await self.session.execute(
            select(Memory)
            .join(MemoryEntityLink, MemoryEntityLink.memory_id == Memory.id)
            .where(
                MemoryEntityLink.entity_id == entity_id,
                Memory.user_id == self.user_id,
                Memory.is_deleted == False,  # noqa: E712
            )
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def extract_and_link_memory(self, memory: Memory, *, use_llm: bool = False) -> list[Entity]:
        extracted = await extract_entities(f"{memory.title}\n{memory.content}", use_llm=use_llm)
        linked: list[Entity] = []
        for item in extracted:
            entity = await self.get_or_create_entity(item.name, item.entity_type)
            await self.link_memory(
                memory.id,
                entity.id,
                relation_type=item.relation_type,
                confidence=item.confidence,
            )
            linked.append(entity)
        return linked

    async def extract_from_text(self, text: str, *, use_llm: bool = False) -> list[Entity]:
        extracted = await extract_entities(text, use_llm=use_llm)
        entities: list[Entity] = []
        for item in extracted:
            entities.append(await self.get_or_create_entity(item.name, item.entity_type))
        return entities

    async def seed_ecosystem(self) -> dict[str, int]:
        """Idempotent seed of known Vikram/Rudra entities and relationships."""
        created_entities = 0
        name_to_id: dict[str, uuid.UUID] = {}

        for item in SEED_ENTITIES:
            before = await self.get_or_create_entity(
                item["name"],
                item["entity_type"],
                description=item.get("description"),
            )
            name_to_id[item["name"]] = before.id
            created_entities += 1

        created_relationships = 0
        for source_name, target_name, rel_type in SEED_RELATIONSHIPS:
            source_id = name_to_id.get(source_name)
            target_id = name_to_id.get(target_name)
            if not source_id or not target_id:
                continue
            existing = await self.session.execute(
                select(GraphRelationship).where(
                    GraphRelationship.user_id == self.user_id,
                    GraphRelationship.source_entity_id == source_id,
                    GraphRelationship.target_entity_id == target_id,
                    GraphRelationship.relation_type == rel_type,
                )
            )
            if existing.scalars().first():
                continue
            await self.create_relationship(source_id, target_id, rel_type)
            created_relationships += 1

        return {"entities": created_entities, "relationships": created_relationships}
