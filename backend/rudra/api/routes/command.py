"""Command center API — primary Rudra interface."""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.base import AgentContext, AgentOrchestrator, AgentType
from rudra.agents.rudra_command import RudraCommandService
from rudra.api.deps import require_auth
from rudra.api.schemas import (
    AgentInfo,
    AgentInvokeRequest,
    AgentResponse,
    CommandRequest,
    CommandResponse,
    HealthResponse,
    ServicesHealthResponse,
)
from rudra.core.config import get_settings
from rudra.core.health import gather_health
from rudra.core.database import get_db
from rudra.memory.models.memory import MemoryType
from rudra.memory.service import MemoryService
from rudra.projects.service import ProjectService
from rudra.security.audit import AuditAction, log_audit

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    settings = get_settings()
    return HealthResponse(
        status="operational",
        version="0.1.0",
        environment=settings.rudra_env,
    )


@router.get("/health/services", response_model=ServicesHealthResponse)
async def health_services():
    """Deep health check across Postgres, Redis, Qdrant, Ollama, and LLM config."""
    return ServicesHealthResponse(**await gather_health())


@router.post("/command", response_model=CommandResponse)
async def execute_command(
    request: CommandRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Primary command interface — the heart of Rudra."""
    orchestrator = AgentOrchestrator()
    rudra = RudraCommandService()
    memory_service = MemoryService(db, user_id)

    recent = await memory_service.list_recent(limit=5)
    memories = [
        {"id": str(m.id), "type": m.memory_type, "title": m.title, "content": m.content}
        for m in recent
    ]

    context_data = dict(request.context)
    project_svc = ProjectService(db, user_id)
    matched_project = await project_svc.find_project_in_text(request.command)
    if matched_project:
        context_data["project_context"] = await project_svc.context_for_agent(matched_project)

    context = AgentContext(
        user_id=user_id,
        session_id=context_data.get("session_id", "default"),
        memories=memories,
        metadata=context_data,
    )

    settings = get_settings()
    lower_cmd = request.command.lower().strip()
    if "good morning" in lower_cmd or lower_cmd in ("morning digest", "morning"):
        from rudra.jarvis.digest import synthesize_spoken_digest

        digest = await synthesize_spoken_digest(db, user_id)
        await log_audit(
            db,
            AuditAction.COMMAND_EXECUTE,
            user_id,
            outcome="success",
            details={"command_preview": request.command[:200], "agent_type": "executive_assistant"},
        )
        return CommandResponse(
            response=digest["text"],
            agent_type="executive_assistant",
            agent_name="Rudra",
            agent_intro="",
            confidence=0.95,
            sources_used=[{"type": "briefing", "title": "spoken_digest"}],
        )

    try:
        if request.agent_type:
            agent_type = AgentType(request.agent_type)
            if (
                settings.command_use_react_for_ea
                and agent_type == AgentType.EXECUTIVE_ASSISTANT
            ):
                from rudra.agents.context_builder import AgentContextBuilder
                from rudra.agents.react import ReActAgent
                from rudra.agents.tools import ToolContext, build_registry_for_agent

                context, sources = await AgentContextBuilder(memory_service).enrich(
                    request.command, agent_type, context
                )
                react = ReActAgent(registry=build_registry_for_agent(agent_type))
                r = await react.run(
                    request.command,
                    ToolContext(user_id=user_id, db=db, brain=react.brain),
                )
                agent = orchestrator.get_agent(agent_type)
                intro, full = agent.format_response(r.answer)
                from rudra.agents.base import AgentResponse
                from rudra.agents.profiles import AGENT_PROFILES

                profile = AGENT_PROFILES[agent_type]
                result = AgentResponse(
                    agent_type=agent_type,
                    content=full,
                    agent_name=agent.name,
                    agent_intro=intro,
                    sources_used=sources,
                    voice_profile={
                        "pitch": profile.voice.pitch,
                        "rate": profile.voice.rate,
                        "voice_hints": list(profile.voice.voice_hints),
                    },
                )
            else:
                result = await rudra.run(request.command, context, user_id, agent_type=agent_type)
        elif request.auto_route:
            result = await rudra.run(request.command, context, user_id)
        else:
            result = await rudra.run(
                request.command, context, user_id, agent_type=AgentType.EXECUTIVE_ASSISTANT
            )
    except RuntimeError:
        # No LLM backend available (no Ollama running, no API keys). Return clear guidance
        # instead of a 500 so the UI can show an actionable message.
        return CommandResponse(
            response=(
                "No AI model is connected yet. Rudra's infrastructure is online, "
                "but it needs a (free) language model to think.\n\n"
                "Pick one:\n"
                "  • Ollama (local, private):  brew install ollama  →  "
                "ollama pull llama3.2 && ollama pull nomic-embed-text\n"
                "  • Gemini free tier:  add GOOGLE_AI_API_KEY to .env "
                "(get a key at https://aistudio.google.com/apikey), then restart the backend."
            ),
            agent_type="system",
            confidence=0.0,
        )

    # Store interaction as episodic memory
    await memory_service.create(
        MemoryType.EPISODIC,
        title=f"Command: {request.command[:80]}",
        content=f"User: {request.command}\n\nRudra ({result.agent_type.value}): {result.content[:2000]}",
        importance=0.6,
        source="command_center",
        tags=["interaction", result.agent_type.value],
    )

    await log_audit(
        db,
        AuditAction.COMMAND_EXECUTE,
        user_id,
        outcome="success",
        details={
            "command_preview": request.command[:200],
            "agent_type": result.agent_type.value,
        },
    )

    # Single-voice contract: the owner always talks to "Rudra"; the routed specialist
    # stays internal (agent_type + routing_analysis remain for the HUD/details drawer).
    return CommandResponse(
        response=result.content,
        agent_type=result.agent_type.value,
        agent_name="Rudra",
        agent_intro="",
        confidence=result.confidence,
        actions=result.actions,
        routing_analysis=result.routing_analysis,
        sources_used=result.sources_used,
        voice_profile=result.voice_profile,
    )


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/command/stream")
async def command_stream(
    request: Request,
    body: CommandRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Streaming command (SSE): route silently, stream ONE Rudra answer, cancellable.

    First tokens appear in ~1–2s. The owner sees a single Rudra voice; the routed
    specialist stays internal (sent only in the meta/done events for the HUD). A client
    disconnect (Stop / AbortController) halts generation server-side.
    """
    from rudra.brain.orchestrator import Message

    memory_service = MemoryService(db, user_id)
    recent = await memory_service.list_recent(limit=5)
    memories = [
        {"id": str(m.id), "type": m.memory_type, "title": m.title, "content": m.content}
        for m in recent
    ]
    ctx_meta = dict(body.context or {})
    base_context = AgentContext(
        user_id=user_id,
        session_id=ctx_meta.get("session_id", "default"),
        memories=memories,
        metadata=ctx_meta,
    )

    rudra = RudraCommandService()
    # Instant silent routing keeps first-token latency low (no extra LLM hop on the stream path).
    agent_type = (
        AgentType(body.agent_type) if body.agent_type else rudra.classify_fast(body.command)[0]
    )

    async def event_stream():
        # Open the connection instantly so the UI reacts in well under a second.
        yield _sse({"type": "meta", "agent_type": agent_type.value, "agent_name": "Rudra"})

        # Bounded enrichment + single-voice Rudra system prompt (its own session).
        system, sources, _ctx = await rudra.enrich_and_build(
            body.command, agent_type, base_context, user_id
        )

        collected: list[str] = []
        try:
            async for chunk in rudra.brain.stream_think(
                [Message(role="user", content=body.command)], system=system
            ):
                if await request.is_disconnected():
                    break
                collected.append(chunk)
                yield _sse({"type": "token", "text": chunk})
        except RuntimeError:
            yield _sse(
                {"type": "token", "text": "No AI model is connected. Start Ollama or set an API key."}
            )
        except Exception as exc:  # noqa: BLE001
            yield _sse({"type": "token", "text": f"[stream error: {exc}]"})

        full = "".join(collected)
        yield _sse(
            {"type": "done", "agent_type": agent_type.value, "agent_name": "Rudra", "sources_used": sources}
        )

        if full:
            try:
                from rudra.core.database import get_session_factory

                async with get_session_factory()() as s2:
                    await MemoryService(s2, user_id).create(
                        MemoryType.EPISODIC,
                        title=f"Command: {body.command[:80]}",
                        content=f"User: {body.command}\n\nRudra: {full[:2000]}",
                        importance=0.6,
                        source="command_center",
                        tags=["interaction", agent_type.value],
                    )
                    await s2.commit()
            except Exception:  # noqa: BLE001
                pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents():
    orchestrator = AgentOrchestrator()
    return [AgentInfo(**a) for a in orchestrator.list_agents()]


@router.post("/agents/invoke", response_model=AgentResponse)
async def invoke_agent(
    request: AgentInvokeRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    orchestrator = AgentOrchestrator()
    memory_service = MemoryService(db, user_id)
    recent = await memory_service.list_recent(limit=5)

    context = AgentContext(
        user_id=user_id,
        session_id=request.session_id or "default",
        memories=[
            {"id": str(m.id), "type": m.memory_type, "title": m.title, "content": m.content}
            for m in recent
        ],
    )

    if request.agent_type:
        result = await orchestrator.invoke(
            AgentType(request.agent_type),
            request.query,
            context,
            memory_service=memory_service,
        )
    else:
        result = await orchestrator.route(request.query, context, memory_service=memory_service)

    return AgentResponse(
        agent_type=result.agent_type.value,
        content=result.content,
        confidence=result.confidence,
        citations=result.citations,
        actions=result.actions,
    )
