"""Jarvis supreme-assistant API — digest, connectors, operators, voice, federation."""

from __future__ import annotations

import base64
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.core.database import get_db
from rudra.jarvis.channels.slack import handle_slack_event, verify_slack_signature
from rudra.jarvis.connectors.registry import ConnectorHub
from rudra.jarvis.digest import synthesize_spoken_digest
from rudra.jarvis.federation import export_memories, import_memories, register_device
from rudra.jarvis.learning import routing_hints_from_traces
from rudra.jarvis.mcp_bridge import call_mcp_tool, list_mcp_servers
from rudra.jarvis.operators import BUILTIN_OPERATORS, load_operator_state
from rudra.jarvis.spec import effective_jarvis_config
from rudra.jarvis.telemetry import log_inference_telemetry
from rudra.memory.hybrid import hybrid_search
from rudra.memory.service import MemoryService
from rudra.skills.loader import get_skill_registry
from rudra.skills.pipeline import skill_catalog_xml
from rudra.voice.service import VoiceService

router = APIRouter(prefix="/jarvis", tags=["jarvis"])


class ConnectRequest(BaseModel):
    provider: str
    refresh_token: str | None = None
    token_json: dict | None = None
    api_token: str | None = None
    api_key: str | None = None
    bot_token: str | None = None


class FederationRegister(BaseModel):
    device_label: str = "device"


class FederationImport(BaseModel):
    sync_token: str
    memories: list[dict] = Field(default_factory=list)


class MCPCallRequest(BaseModel):
    server: str
    tool: str
    arguments: dict = Field(default_factory=dict)


class VoiceTranscribeRequest(BaseModel):
    session_id: str = "default"
    text: str | None = None


@router.get("/config")
async def jarvis_config(user_id: str = Depends(require_auth)):
    return effective_jarvis_config()


@router.get("/connectors")
async def list_connectors(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    from rudra.integrations.executive import ExecutiveCommandService

    return await ExecutiveCommandService(db, user_id).list_connector_status()


@router.post("/connect")
async def connect_provider(
    body: ConnectRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    from rudra.integrations.executive import ExecutiveCommandService

    creds = body.model_dump(exclude={"provider"}, exclude_none=True)
    result = await ExecutiveCommandService(db, user_id).connect_provider(body.provider, **creds)
    await db.commit()
    return result


@router.post("/digest/spoken")
async def spoken_digest(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    result = await synthesize_spoken_digest(db, user_id)
    await db.commit()
    return result


@router.post("/research/spoken")
async def spoken_research_brief(
    topic: str | None = None,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    from rudra.jarvis.research_digest import synthesize_spoken_research_brief

    result = await synthesize_spoken_research_brief(db, user_id, topic=topic)
    await db.commit()
    return result


@router.post("/librarian/spoken")
async def spoken_librarian(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    from rudra.jarvis.domain_digests import spoken_librarian_brief

    result = await spoken_librarian_brief(db, user_id)
    await db.commit()
    return result


@router.post("/concierge/spoken")
async def spoken_concierge(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    from rudra.jarvis.domain_digests import spoken_concierge_brief

    result = await spoken_concierge_brief(db, user_id)
    await db.commit()
    return result


@router.post("/travel/spoken")
async def spoken_travel(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    from rudra.jarvis.domain_digests import spoken_travel_brief

    result = await spoken_travel_brief(db, user_id)
    await db.commit()
    return result


@router.post("/luxury/spoken")
async def spoken_luxury(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    from rudra.jarvis.domain_digests import spoken_luxury_brief

    result = await spoken_luxury_brief(db, user_id)
    await db.commit()
    return result


@router.post("/writing/spoken")
async def spoken_writing(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    from rudra.jarvis.domain_digests import spoken_writing_brief

    result = await spoken_writing_brief(db, user_id)
    await db.commit()
    return result


@router.post("/presentation/spoken")
async def spoken_presentation(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    from rudra.jarvis.domain_digests import spoken_deck_brief

    result = await spoken_deck_brief(db, user_id)
    await db.commit()
    return result


@router.post("/operations/spoken")
async def spoken_operations(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    from rudra.jarvis.domain_digests import spoken_ops_brief

    result = await spoken_ops_brief(db, user_id)
    await db.commit()
    return result


@router.get("/digest/audio")
async def digest_audio(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    result = await synthesize_spoken_digest(db, user_id)
    await db.commit()
    audio = result.get("audio", {})
    if audio.get("mode") == "file" and audio.get("base64"):
        return Response(content=base64.b64decode(audio["base64"]), media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="TTS audio unavailable — use text mode or set OPENAI_API_KEY")


@router.get("/operators")
async def list_operators(user_id: str = Depends(require_auth)):
    return BUILTIN_OPERATORS


@router.get("/operators/{operator_id}/state")
async def operator_state(
    operator_id: str,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await load_operator_state(db, user_id, operator_id)


@router.get("/learning/routing-hints")
async def routing_hints(user_id: str = Depends(require_auth)):
    return routing_hints_from_traces()


@router.get("/skills/catalog")
async def skills_catalog(user_id: str = Depends(require_auth)):
    reg = get_skill_registry()
    return {"catalog_xml": skill_catalog_xml(reg.list()), "skills": reg.list()}


@router.get("/mcp/servers")
async def mcp_servers(user_id: str = Depends(require_auth)):
    return list_mcp_servers()


@router.post("/mcp/call")
async def mcp_call(body: MCPCallRequest, user_id: str = Depends(require_auth)):
    return {"result": await call_mcp_tool(body.server, body.tool, body.arguments)}


@router.post("/federation/register")
async def federation_register(
    body: FederationRegister,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    creds = await register_device(db, user_id, body.device_label)
    await db.commit()
    return creds


@router.get("/federation/export")
async def federation_export(
    sync_token: str,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await export_memories(db, user_id, sync_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    await db.commit()
    return {"memories": data, "count": len(data)}


@router.post("/federation/import")
async def federation_import(
    body: FederationImport,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    try:
        count = await import_memories(db, user_id, body.sync_token, body.memories)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    await db.commit()
    return {"imported": count}


@router.post("/memory/hybrid-search")
async def jarvis_hybrid_search(
    query: str,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = MemoryService(db, user_id)
    hits = await hybrid_search(svc, query, limit=10)
    return [
        {"id": str(m.id), "title": m.title, "score": round(score, 3), "preview": m.content[:200]}
        for m, score in hits
    ]


@router.post("/voice/transcribe")
async def voice_transcribe(body: VoiceTranscribeRequest, user_id: str = Depends(require_auth)):
    svc = VoiceService()
    if body.text:
        return {"transcript": body.text, "mode": "text_fallback"}
    return await svc.process_audio(body.session_id, b"")


@router.post("/channels/slack/events")
async def slack_events(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Slack-Signature", "")
    ts = request.headers.get("X-Slack-Request-Timestamp", "0")
    if not verify_slack_signature(body, ts, sig):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")
    payload = json.loads(body.decode("utf-8"))
    return await handle_slack_event(payload)


@router.get("/telemetry/recent")
async def recent_telemetry(user_id: str = Depends(require_auth)):
    from pathlib import Path
    import json

    from rudra.core.config import get_settings

    p = Path(get_settings().data_dir) / "telemetry.jsonl"
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()[-20:]
    return [json.loads(ln) for ln in lines if ln.strip()]
