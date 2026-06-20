"""Rudra FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from rudra.api.routes import agent, auth, autonomy, command, documents, domains, graph, integrations, jarvis, memory, openai_compat, projects, research, skills
from rudra.auth.service import AuthService
from rudra.graph.service import GraphService
from rudra.projects.service import ProjectService
from rudra.autonomy.scheduler import get_scheduler
from rudra.core.config import get_settings
from rudra.core.database import get_session_factory, lifespan as db_lifespan
from rudra.core.logging import get_logger
from rudra.core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Wrap the DB lifespan and start/stop the in-process autonomy scheduler (P3)."""
    async with db_lifespan(app):
        # Bootstrap owner account for local-first single-user auth.
        factory = get_session_factory()
        async with factory() as session:
            await AuthService(session).ensure_owner_user()
            try:
                await GraphService(session, "owner").seed_ecosystem()
            except Exception as exc:
                logger.warning("graph_seed_skipped", error=str(exc))
            try:
                await ProjectService(session, "owner").seed_projects()
            except Exception as exc:
                logger.warning("project_seed_skipped", error=str(exc))
            try:
                from rudra.agents.data.seed import seed_agent_phase_data

                await seed_agent_phase_data(session, "owner")
            except Exception as exc:
                logger.warning("agent_data_seed_skipped", error=str(exc))
            try:
                from rudra.jarvis.operators import register_operators

                register_operators()
            except Exception as exc:
                logger.warning("operators_register_skipped", error=str(exc))
            await session.commit()

        scheduler = None
        if get_settings().enable_scheduler:
            scheduler = get_scheduler()
            await scheduler.start()
        try:
            yield
        finally:
            if scheduler is not None:
                await scheduler.stop()

app = FastAPI(
    title="Rudra",
    description="Personal Intelligence Operating System",
    version="0.1.0",
    lifespan=lifespan,
)

_settings = get_settings()
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=_settings.rate_limit_per_minute)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins_list,
    allow_origin_regex=_settings.cors_allow_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(command.router, prefix="/api/v1", tags=["command"])
app.include_router(graph.router, prefix="/api/v1", tags=["graph"])
app.include_router(memory.router, prefix="/api/v1", tags=["memory"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(integrations.router, prefix="/api/v1", tags=["integrations"])
app.include_router(jarvis.router, prefix="/api/v1", tags=["jarvis"])
app.include_router(openai_compat.router, prefix="/api", tags=["openai-compat"])
app.include_router(research.router, prefix="/api/v1", tags=["research"])
app.include_router(domains.router, prefix="/api/v1", tags=["domains"])
app.include_router(agent.router, prefix="/api/v1", tags=["agent"])
app.include_router(skills.router, prefix="/api/v1", tags=["skills"])
app.include_router(autonomy.router, prefix="/api/v1", tags=["autonomy"])


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time command stream — continuous context retention."""
    await websocket.accept()
    logger.info("ws_connected")
    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("command", "")

            from rudra.agents.base import AgentContext, AgentOrchestrator

            orchestrator = AgentOrchestrator()
            context = AgentContext(
                user_id="owner",
                session_id=data.get("session_id", "ws-default"),
            )
            result = await orchestrator.route(command, context)

            await websocket.send_json({
                "type": "response",
                "agent_type": result.agent_type.value,
                "content": result.content,
                "confidence": result.confidence,
            })
    except WebSocketDisconnect:
        logger.info("ws_disconnected")
