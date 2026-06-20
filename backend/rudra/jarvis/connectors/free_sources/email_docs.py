"""Email and document free sources — IMAP, Obsidian vault, Internet Archive."""

from __future__ import annotations

import asyncio
import imaplib
import email
from datetime import datetime
from email.header import decode_header
from pathlib import Path

from rudra.core.config import Settings
from rudra.integrations.providers import DocumentRef, EmailMessage
from rudra.jarvis.connectors.free_sources._http import get_json


def _decode_header(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out: list[str] = []
    for chunk, enc in parts:
        if isinstance(chunk, bytes):
            out.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(str(chunk))
    return "".join(out)


def _imap_fetch_sync(settings: Settings, *, limit: int) -> list[EmailMessage]:
    host = settings.ea_imap_host
    user = settings.ea_imap_user
    pwd = settings.ea_imap_password
    if not (host and user and pwd):
        return []
    try:
        mail = imaplib.IMAP4_SSL(host, settings.ea_imap_port)
        mail.login(user, pwd.get_secret_value())
        mail.select("INBOX")
        _, data = mail.search(None, "ALL")
        ids = data[0].split()[-limit:]
        out: list[EmailMessage] = []
        for num in reversed(ids):
            _, msg_data = mail.fetch(num, "(RFC822)")
            if not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            subject = _decode_header(msg.get("Subject"))
            sender = _decode_header(msg.get("From"))
            date_hdr = msg.get("Date", "")
            try:
                received = parsedate_to_datetime(date_hdr).strftime("%Y-%m-%d %H:%M")
            except Exception:
                received = datetime.now().strftime("%Y-%m-%d %H:%M")
            snippet = subject[:160]
            out.append(
                EmailMessage(
                    sender[:80],
                    subject[:120],
                    snippet,
                    received,
                    "urgent" in subject.lower() or "action" in subject.lower(),
                    "imap",
                )
            )
        mail.logout()
        return out
    except Exception:
        return []


async def fetch_imap_emails(settings: Settings, *, limit: int = 8) -> list[EmailMessage]:
    return await asyncio.to_thread(_imap_fetch_sync, settings, limit=limit)


async def fetch_obsidian_documents(settings: Settings, *, limit: int = 10) -> list[DocumentRef]:
    vault = settings.ea_obsidian_vault_path
    if not vault:
        return []
    root = Path(vault)
    if not root.is_dir():
        return []
    md_files = sorted(root.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    out: list[DocumentRef] = []
    for path in md_files[:limit]:
        mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
        rel = str(path.relative_to(root))
        out.append(DocumentRef(rel[:120], url=str(path), modified_at=mtime, provider="obsidian"))
    return out


async def fetch_archive_context(settings: Settings, *, query: str = "technology", limit: int = 3) -> list[DocumentRef]:
    data = await get_json(
        "https://archive.org/advancedsearch.php",
        params={
            "q": query,
            "fl[]": "identifier,title,date",
            "rows": limit,
            "output": "json",
        },
    )
    if not isinstance(data, dict):
        return []
    docs = data.get("response", {}).get("docs", [])
    return [
        DocumentRef(
            d.get("title", d.get("identifier", "Archive"))[:120],
            url=f"https://archive.org/details/{d.get('identifier')}",
            modified_at=d.get("date"),
            provider="internet_archive",
        )
        for d in docs[:limit]
    ]
