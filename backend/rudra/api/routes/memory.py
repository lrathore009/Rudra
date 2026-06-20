"""Memory API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.api.schemas import MemoryCreate, MemoryResponse, MemorySearchRequest
from rudra.core.database import get_db
from rudra.graph.service import GraphService
from rudra.memory.models.memory import MemoryType
from rudra.memory.service import MemoryService
from rudra.security.audit import AuditAction, log_audit

router = APIRouter(prefix="/memories", tags=["memory"])


@router.post("", response_model=MemoryResponse)
async def create_memory(
    data: MemoryCreate,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    service = MemoryService(db, user_id)
    memory = await service.create(
        MemoryType(data.memory_type),
        data.title,
        data.content,
        summary=data.summary,
        importance=data.importance,
        source=data.source,
        tags=data.tags,
        metadata=data.metadata,
    )
    await log_audit(db, AuditAction.MEMORY_CREATE, user_id, resource_id=str(memory.id))
    try:
        await GraphService(db, user_id).extract_and_link_memory(memory)
    except Exception:
        pass
    return memory


@router.post("/search", response_model=list[MemoryResponse])
async def search_memories(
    req: MemorySearchRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Semantic memory search. Embeds the query and ranks by vector similarity;
    gracefully falls back to recent memories if no embedding backend is available."""
    service = MemoryService(db, user_id)
    mt = MemoryType(req.memory_type) if req.memory_type else None
    results = await service.search_by_text(
        req.query, memory_type=mt, limit=req.limit, min_similarity=0.0
    )
    return [m for m, _score in results]


@router.get("", response_model=list[MemoryResponse])
async def list_memories(
    memory_type: str | None = None,
    limit: int = 20,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    service = MemoryService(db, user_id)
    mt = MemoryType(memory_type) if memory_type else None
    return await service.list_recent(memory_type=mt, limit=limit)


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: uuid.UUID,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    service = MemoryService(db, user_id)
    memory = await service.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    await log_audit(
        db, AuditAction.MEMORY_READ, user_id, resource_id=str(memory_id)
    )
    return memory


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: uuid.UUID,
    hard: bool = False,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    service = MemoryService(db, user_id)
    deleted = await service.delete(memory_id, hard=hard)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    await log_audit(
        db,
        AuditAction.MEMORY_DELETE,
        user_id,
        resource_id=str(memory_id),
        details={"hard_delete": hard},
    )
    return {"status": "deleted", "id": str(memory_id)}
