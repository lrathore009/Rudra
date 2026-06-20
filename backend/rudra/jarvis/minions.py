"""#8 — Minions-style local/cloud collaboration with mandatory redaction."""

from __future__ import annotations

import re

from rudra.brain.orchestrator import Brain, Message
from rudra.jarvis.guardrails import scan_and_redact
from rudra.jarvis.persona import jarvis_system_prompt

_COMPLEXITY_HINTS = re.compile(
    r"\b(research|analyze|compare|strategy|architecture|invest|legal|contract|"
    r"forecast|synthesize|deep dive|multi.?step)\b",
    re.I,
)


def classify_complexity(query: str) -> str:
    """Return 'cloud' for hard reasoning, 'local' for routine chief-of-staff tasks."""
    if len(query) > 400 or _COMPLEXITY_HINTS.search(query):
        return "cloud"
    return "local"


async def minions_think(
    brain: Brain,
    query: str,
    *,
    context: str = "",
    system: str | None = None,
) -> tuple[str, str]:
    """Local extracts context; cloud reasons when complexity warrants it."""
    tier = classify_complexity(query)
    local_system = system or jarvis_system_prompt(mode="command")
    local_prompt = query
    if context:
        local_prompt = f"Context:\n{context[:6000]}\n\nTask:\n{query}"

    if tier == "local":
        result = await brain.think(
            [Message(role="user", content=local_prompt)],
            system=local_system,
            model_tier="fast",
        )
        return result.content, "local"

    # Cloud path: redact personal context, send compressed task to reasoning tier.
    safe_context = scan_and_redact(context or query[:8000]).redacted_text
    cloud_prompt = (
        f"Owner context (redacted):\n{safe_context[:4000]}\n\n"
        f"Produce a thorough executive-grade answer:\n{query}"
    )
    result = await brain.think(
        [Message(role="user", content=cloud_prompt)],
        system=local_system,
        model_tier="reasoning",
    )
    return result.content, "cloud"
