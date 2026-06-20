"""Document Brain service — ingest, chunk, embed, search."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.core.config import get_settings
from rudra.documents.extractor import extract_text
from rudra.documents.models import Document, DocumentChunk, DocumentEntity, DocumentStatus
from rudra.graph.service import GraphService


class DocumentService:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.settings = get_settings()
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for d in (
            self.settings.uploads_dir,
            self.settings.processed_dir,
            self.settings.document_chunks_dir,
        ):
            Path(d).mkdir(parents=True, exist_ok=True)

    async def list_documents(self, *, limit: int = 50) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.user_id == self.user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_document(self, document_id: uuid.UUID) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id, Document.user_id == self.user_id)
        )
        return result.scalar_one_or_none()

    async def ingest_upload(
        self,
        *,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> Document:
        uploads = Path(self.settings.uploads_dir)
        safe_name = re.sub(r"[^\w.\-]+", "_", filename)[:200]
        doc = Document(
            user_id=self.user_id,
            filename=safe_name,
            content_type=content_type or "application/octet-stream",
            file_path="",
            status=DocumentStatus.PROCESSING.value,
        )
        self.session.add(doc)
        await self.session.flush()

        dest = uploads / f"{doc.id}_{safe_name}"
        dest.write_bytes(data)
        doc.file_path = str(dest)

        try:
            raw, page_count = extract_text(dest, content_type)
            doc.page_count = page_count
            doc.char_count = len(raw)
            processed_path = Path(self.settings.processed_dir) / f"{doc.id}.txt"
            processed_path.write_text(raw, encoding="utf-8")
            await self._chunk_and_embed(doc, raw)
            await self._link_entities(doc, raw)
            doc.status = DocumentStatus.READY.value
        except Exception as exc:  # noqa: BLE001
            doc.status = DocumentStatus.FAILED.value
            doc.error_message = str(exc)[:500]
        await self.session.flush()
        return doc

    def _split_chunks(self, raw: str) -> list[str]:
        size = self.settings.document_chunk_size
        overlap = self.settings.document_chunk_overlap
        chunks: list[str] = []
        start = 0
        while start < len(raw):
            end = min(len(raw), start + size)
            piece = raw[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= len(raw):
                break
            start = max(start + 1, end - overlap)
        return chunks or [raw[:size]]

    async def _chunk_and_embed(self, doc: Document, raw: str) -> None:
        from rudra.brain.embeddings import embed_text

        pieces = self._split_chunks(raw)
        for idx, piece in enumerate(pieces):
            embedding = None
            try:
                embedding = await embed_text(piece)
            except Exception:
                embedding = None
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=piece,
                embedding=embedding,
                token_estimate=max(1, len(piece) // 4),
            )
            self.session.add(chunk)
        await self.session.flush()

    async def _link_entities(self, doc: Document, raw: str) -> None:
        graph = GraphService(self.session, self.user_id)
        entities = await graph.extract_from_text(raw[:4000])
        for entity in entities:
            self.session.add(
                DocumentEntity(document_id=doc.id, entity_id=entity.id, confidence=0.8)
            )

    async def search(self, query: str, *, limit: int = 8) -> list[tuple[DocumentChunk, Document, float]]:
        from rudra.brain.embeddings import embed_text

        embedding = await embed_text(query)
        sql = text(
            """
            SELECT c.id, 1 - (c.embedding <=> CAST(:embedding AS vector)) AS score
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.user_id = :user_id
              AND c.embedding IS NOT NULL
              AND d.status = 'ready'
            ORDER BY c.embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """
        )
        rows = await self.session.execute(
            sql,
            {"user_id": self.user_id, "embedding": str(embedding), "limit": limit},
        )
        hits: list[tuple[DocumentChunk, Document, float]] = []
        for row in rows:
            chunk = await self.session.get(DocumentChunk, row.id)
            if chunk is None:
                continue
            doc = await self.get_document(chunk.document_id)
            if doc:
                hits.append((chunk, doc, float(row.score)))
        return hits

    async def summarize(self, document_id: uuid.UUID) -> str:
        doc = await self.get_document(document_id)
        if doc is None:
            raise ValueError("Document not found")
        result = await self.session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .limit(6)
        )
        chunks = list(result.scalars().all())
        excerpt = "\n\n".join(c.content[:600] for c in chunks)
        from rudra.brain.orchestrator import Brain

        brain = Brain()
        completion = await brain.think(
            [{"role": "user", "content": f"Summarize this document in 5 bullet points:\n\n{excerpt}"}],
            model_tier="fast",
        )
        doc.summary = completion.content
        await self.session.flush()
        return completion.content

    async def ask(self, query: str, *, document_id: uuid.UUID | None = None) -> dict[str, Any]:
        if document_id:
            doc = await self.get_document(document_id)
            if doc is None:
                return {"answer": "Document not found.", "citations": []}
            result = await self.session.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
                .limit(6)
            )
            chunks = list(result.scalars().all())
            hits = [(chunk, doc, 1.0) for chunk in chunks]
        else:
            hits = await self.search(query, limit=6)
        if not hits:
            return {"answer": "No relevant document passages found.", "citations": []}

        context = "\n\n".join(
            f"[{i}] ({doc.filename}) {chunk.content[:700]}"
            for i, (chunk, doc, _score) in enumerate(hits, 1)
        )
        from rudra.brain.orchestrator import Brain

        brain = Brain()
        completion = await brain.think(
            [
                {
                    "role": "user",
                    "content": (
                        "Answer using ONLY the cited passages. Include [n] citations.\n\n"
                        f"Question: {query}\n\nPassages:\n{context}"
                    ),
                }
            ],
            model_tier="default",
        )
        citations = [
            {
                "index": i,
                "document_id": str(doc.id),
                "filename": doc.filename,
                "chunk_index": chunk.chunk_index,
                "excerpt": chunk.content[:240],
            }
            for i, (chunk, doc, score) in enumerate(hits, 1)
        ]
        return {"answer": completion.content, "citations": citations}
