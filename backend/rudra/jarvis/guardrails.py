"""#9 — Security guardrails: PII/secret scan before cloud transmission."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rudra.jarvis.events import EventType, get_event_bus

_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_PHONE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
_API_KEY = re.compile(r"\b(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AIza[A-Za-z0-9_-]{20,})\b")


@dataclass
class ScanResult:
    redacted_text: str
    findings: list[str]
    blocked: bool = False


def scan_and_redact(text: str, *, mode: str = "redact") -> ScanResult:
    findings: list[str] = []
    out = text
    for label, pattern in (("email", _EMAIL), ("phone", _PHONE), ("secret", _API_KEY)):
        if pattern.search(out):
            findings.append(label)
            if mode == "redact":
                out = pattern.sub(f"[REDACTED_{label.upper()}]", out)
    get_event_bus().publish(
        EventType.SECURITY_SCAN,
        {"findings": findings, "length": len(text)},
    )
    return ScanResult(redacted_text=out, findings=findings, blocked=mode == "block" and bool(findings))
