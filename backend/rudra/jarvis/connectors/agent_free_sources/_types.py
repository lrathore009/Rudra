"""Shared types for specialist agent free intelligence feeds."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IntelItem:
    title: str
    content: str
    provider: str
    category: str = "intel"
    url: str | None = None
    metadata: dict | None = field(default=None)
