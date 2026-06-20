"""Knowledge graph API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.api.schemas import MemoryResponse
from rudra.core.database import get_db
from rudra.graph.models import GraphRelationType
from rudra.graph.service import GraphService

router = APIRouter(prefix="/graph", tags=["graph"])


class EntityResponse(BaseModel):
    id: uuid.UUID
    name: str
    entity_type: str
    description: str | None = None

    model_config = {"from_attributes": True}


class RelationshipResponse(BaseModel):
    id: uuid.UUID
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    relation_type: str
    weight: float
    notes: str | None = None

    model_config = {"from_attributes": True}


class RelationshipCreate(BaseModel):
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    relation_type: str = GraphRelationType.RELATED_TO.value
    weight: float = 1.0
    notes: str | None = None


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1)
    use_llm: bool = False


@router.get("/entities", response_model=list[EntityResponse])
async def list_entities(
    q: str | None = None,
    entity_type: str | None = None,
    limit: int = 50,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    graph = GraphService(db, user_id)
    return await graph.list_entities(query=q, entity_type=entity_type, limit=limit)


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: uuid.UUID,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    graph = GraphService(db, user_id)
    entity = await graph.get_entity(entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.get("/entities/{entity_id}/memories", response_model=list[MemoryResponse])
async def entity_memories(
    entity_id: uuid.UUID,
    limit: int = 20,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    graph = GraphService(db, user_id)
    if await graph.get_entity(entity_id) is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return await graph.memories_for_entity(entity_id, limit=limit)


@router.get("/relationships", response_model=list[RelationshipResponse])
async def list_relationships(
    entity_id: uuid.UUID | None = None,
    limit: int = 100,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    graph = GraphService(db, user_id)
    return await graph.list_relationships(entity_id=entity_id, limit=limit)


@router.post("/relationships", response_model=RelationshipResponse)
async def create_relationship(
    body: RelationshipCreate,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    graph = GraphService(db, user_id)
    if await graph.get_entity(body.source_entity_id) is None:
        raise HTTPException(status_code=404, detail="Source entity not found")
    if await graph.get_entity(body.target_entity_id) is None:
        raise HTTPException(status_code=404, detail="Target entity not found")
    return await graph.create_relationship(
        body.source_entity_id,
        body.target_entity_id,
        body.relation_type,
        weight=body.weight,
        notes=body.notes,
    )


@router.post("/extract", response_model=list[EntityResponse])
async def extract_entities(
    body: ExtractRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    graph = GraphService(db, user_id)
    return await graph.extract_from_text(body.text, use_llm=body.use_llm)
