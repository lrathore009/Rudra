"""Document Brain API routes."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.core.database import get_db
from rudra.documents.service import DocumentService
from rudra.security.audit import AuditAction, log_audit

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    status: str
    page_count: int | None
    char_count: int | None
    summary: str | None
    error_message: str | None

    model_config = {"from_attributes": True}


class DocumentSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = 8


class DocumentAskRequest(BaseModel):
    query: str = Field(min_length=1)
    document_id: uuid.UUID | None = None


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    data = await file.read()
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 20MB)")
    svc = DocumentService(db, user_id)
    doc = await svc.ingest_upload(
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
        data=data,
    )
    await log_audit(
        db,
        AuditAction.DOCUMENT_UPLOAD,
        user_id,
        resource_id=str(doc.id),
        details={"filename": doc.filename, "status": doc.status},
    )
    return doc


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService(db, user_id).list_documents()


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    doc = await DocumentService(db, user_id).get_document(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/{document_id}/summarize")
async def summarize_document(
    document_id: uuid.UUID,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = DocumentService(db, user_id)
    try:
        summary = await svc.summarize(document_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Document not found") from None
    return {"document_id": str(document_id), "summary": summary}


@router.post("/search")
async def search_documents(
    body: DocumentSearchRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    hits = await DocumentService(db, user_id).search(body.query, limit=body.limit)
    return [
        {
            "document_id": str(doc.id),
            "filename": doc.filename,
            "chunk_index": chunk.chunk_index,
            "score": score,
            "excerpt": chunk.content[:300],
        }
        for chunk, doc, score in hits
    ]


@router.post("/ask")
async def ask_documents(
    body: DocumentAskRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService(db, user_id).ask(body.query, document_id=body.document_id)
