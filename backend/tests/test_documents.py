"""Document Brain tests."""

import io

import pytest
from sqlalchemy import func, select

from rudra.documents.extractor import extract_text
from rudra.documents.models import DocumentChunk


def test_text_extraction(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("Rudra OS document brain test.", encoding="utf-8")
    text, pages = extract_text(path, "text/plain")
    assert "Rudra OS" in text
    assert pages is None


def test_upload_and_list(client, require_db, stub_embeddings):
    payload = io.BytesIO(b"Rudra OS stores founder knowledge locally and securely.")
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("brief.txt", payload, "text/plain")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ready"
    listed = client.get("/api/v1/documents")
    assert listed.status_code == 200
    assert any(d["filename"] == "brief.txt" for d in listed.json())


def test_document_search(client, require_db, stub_embeddings):
    payload = io.BytesIO(b"ChemSphere roadmap includes API design and pilot launch.")
    client.post(
        "/api/v1/documents/upload",
        files={"file": ("chem.txt", payload, "text/plain")},
    )
    res = client.post("/api/v1/documents/search", json={"query": "ChemSphere roadmap"})
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_document_ask(client, require_db, stub_embeddings, stub_llm):
    payload = io.BytesIO(b"Jobsflix Nexus AI connects recruiters with semantic search.")
    up = client.post(
        "/api/v1/documents/upload",
        files={"file": ("nexus.txt", payload, "text/plain")},
    )
    doc_id = up.json()["id"]
    res = client.post(
        "/api/v1/documents/ask",
        json={"query": "What does Nexus AI do?", "document_id": doc_id},
    )
    assert res.status_code == 200
    body = res.json()
    assert "answer" in body
    assert body["citations"]


def test_upload_requires_auth(client, require_db, monkeypatch):
    payload = io.BytesIO(b"secret")
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    from rudra.core.config import get_settings

    get_settings.cache_clear()
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("secret.txt", payload, "text/plain")},
    )
    assert res.status_code == 401
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_chunk_created(require_db, stub_embeddings):
    from rudra.core.database import get_session_factory
    from rudra.documents.service import DocumentService

    factory = get_session_factory()
    async with factory() as session:
        svc = DocumentService(session, "owner")
        doc = await svc.ingest_upload(
            filename="chunk.txt",
            content_type="text/plain",
            data=b"word " * 400,
        )
        await session.commit()
        count = await session.execute(
            select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc.id)
        )
        assert (count.scalar_one() or 0) >= 1
