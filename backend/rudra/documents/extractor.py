"""Text extraction from uploaded files."""

from __future__ import annotations

from pathlib import Path


def extract_text(path: Path, content_type: str) -> tuple[str, int | None]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown"} or "text" in content_type:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text, None
    if suffix == ".pdf" or content_type == "application/pdf":
        return _extract_pdf(path)
    if suffix == ".docx" or "wordprocessingml" in content_type:
        return _extract_docx(path)
    raise ValueError(f"Unsupported file type: {suffix or content_type}")


def _extract_pdf(path: Path) -> tuple[str, int | None]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip(), len(reader.pages)


def _extract_docx(path: Path) -> tuple[str, int | None]:
    from docx import Document

    doc = Document(str(path))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return text.strip(), None
