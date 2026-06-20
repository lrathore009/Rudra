"""Jarvis spoken research brief."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from rudra.brain.orchestrator import Brain, Message
from rudra.jarvis.events import EventType, get_event_bus
from rudra.jarvis.persona import jarvis_system_prompt
from rudra.jarvis.tts import synthesize_speech
from rudra.research.reports import ResearchReportService


async def synthesize_spoken_research_brief(
    session: AsyncSession,
    user_id: str,
    *,
    topic: str | None = None,
    brain: Brain | None = None,
) -> dict:
    library = ResearchReportService(session, user_id)
    trends = await library.trends()
    if topic:
        from rudra.research.hybrid import hybrid_search_reports

        hits = await hybrid_search_reports(library, topic, limit=3)
        reports = [r for r, _ in hits]
    else:
        reports = await library.list_recent(limit=5)

    blocks = ["## Research Library Snapshot", f"Reports: {trends['count']}, avg confidence: {trends['avg_confidence']}"]
    blocks.append(f"Stale (>30d): {trends['stale_count']}")
    for r in reports[:5]:
        blocks.append(f"- {r.title} (conf={r.confidence_score:.2f})")

    raw = "\n".join(blocks)
    brain = brain or Brain()
    result = await brain.think(
        [Message(role="user", content=f"Synthesize a spoken research briefing:\n\n{raw}")],
        system=jarvis_system_prompt(mode="research"),
        model_tier="fast",
    )
    audio = await synthesize_speech(result.content)
    get_event_bus().publish(
        EventType.RESEARCH_COMPLETED,
        {"user_id": user_id, "spoken": True, "chars": len(result.content)},
    )
    return {"text": result.content, "sources_preview": raw[:1500], "audio": audio, "trends": trends}
