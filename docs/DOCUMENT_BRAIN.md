# Document Brain

Ingest, chunk, embed, search, and Q&A over local documents.

## Storage

| Path | Purpose |
|------|---------|
| `data/uploads/` | Raw uploads |
| `data/processed/` | Extracted plain text |
| `data/document_chunks/` | Reserved for future file exports |

Configure via `UPLOADS_DIR`, `PROCESSED_DIR`, `DOCUMENT_CHUNKS_DIR` in `.env`.

## Supported formats

- TXT, Markdown
- PDF (`pypdf`)
- DOCX (`python-docx`)

## APIs

- `POST /api/v1/documents/upload`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{id}`
- `POST /api/v1/documents/{id}/summarize`
- `POST /api/v1/documents/search`
- `POST /api/v1/documents/ask`

All routes require authentication when `AUTH_REQUIRED=true`.

## Agent tools

- `search_documents` — semantic chunk search
- `summarize_document` — LLM summary by document id

## HUD

**Document Brain** panel: upload, document list, processing status, ask interface with citations.

## Linking

Uploaded documents auto-link to knowledge graph entities during ingestion.
