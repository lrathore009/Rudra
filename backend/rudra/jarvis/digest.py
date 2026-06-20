"""#1 — Spoken morning digest synthesis with Jarvis persona."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from rudra.brain.orchestrator import Brain, Message
from rudra.integrations.service import BriefingService, IntegrationService
from rudra.jarvis.events import EventType, get_event_bus
from rudra.jarvis.persona import jarvis_system_prompt
from rudra.jarvis.tts import synthesize_speech
from rudra.projects.service import ProjectService


async def collect_digest_sources(session: AsyncSession, user_id: str) -> str:
    briefing_svc = BriefingService(session, user_id)
    briefing = await briefing_svc.get_latest()
    if briefing is None:
        briefing = await briefing_svc.generate_daily()

    integrations = IntegrationService(session, user_id)
    events = await integrations.calendar_events()
    emails = await integrations.recent_emails(limit=5)
    dashboard = await ProjectService(session, user_id).dashboard()

    blocks = [briefing.content, "", "## Calendar"]
    for e in events[:5]:
        blocks.append(f"- {e.starts_at} {e.title}")
    blocks.extend(["", "## Attention emails"])
    for m in emails:
        if m.needs_attention:
            blocks.append(f"- {m.sender}: {m.subject}")
    blocks.extend(["", f"Stale projects: {dashboard['stale_count']}"])
    return "\n".join(blocks)


async def synthesize_spoken_digest(session: AsyncSession, user_id: str, brain: Brain | None = None) -> dict:
    raw = await collect_digest_sources(session, user_id)
    brain = brain or Brain()
    result = await brain.think(
        [Message(role="user", content=f"Synthesize this into a spoken briefing:\n\n{raw}")],
        system=jarvis_system_prompt(mode="digest"),
        model_tier="fast",
    )
    audio = await synthesize_speech(result.content)
    get_event_bus().publish(
        EventType.BRIEFING_GENERATED,
        {"user_id": user_id, "chars": len(result.content)},
    )
    return {"text": result.content, "sources_preview": raw[:1500], "audio": audio}
