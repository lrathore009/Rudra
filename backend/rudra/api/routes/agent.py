"""P1 — autonomous tool-using agent endpoint (ReAct loop)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.agents.react import ReActAgent
from rudra.agents.tools import ToolContext, build_default_registry, build_registry_for_agent
from rudra.agents.types import AgentType
from rudra.api.deps import require_auth
from rudra.autonomy.traces import Trace, log_trace
from rudra.core.database import get_db

router = APIRouter()


class ActRequest(BaseModel):
    query: str
    max_steps: int | None = None
    agent_type: str | None = None


class ActStep(BaseModel):
    thought: str
    tool: str | None = None
    args: dict = {}
    observation: str | None = None


class ActResponse(BaseModel):
    answer: str
    steps: list[ActStep]
    tools_used: list[str]
    model: str
    latency_ms: int
    completed: bool


@router.get("/agent/tools")
async def list_tools(agent_type: str | None = None):
    """List tools available to the autonomous agent (optionally per specialist)."""
    if agent_type:
        return build_registry_for_agent(AgentType(agent_type)).list()
    return build_default_registry().list()


@router.post("/agent/act", response_model=ActResponse)
async def agent_act(
    request: ActRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Run the ReAct tool-using loop on a task; return the answer + reasoning trace."""
    registry = (
        build_registry_for_agent(AgentType(request.agent_type))
        if request.agent_type
        else build_default_registry()
    )
    agent = ReActAgent(registry=registry, max_steps=request.max_steps)
    ctx = ToolContext(user_id=user_id, db=db, brain=agent.brain)
    try:
        result = await agent.run(request.query, ctx)
    except RuntimeError:
        return ActResponse(
            answer=(
                "No AI model is connected yet. Start Ollama (ollama pull llama3.2) or set "
                "an API key in .env, then retry."
            ),
            steps=[],
            tools_used=[],
            model="none",
            latency_ms=0,
            completed=False,
        )

    log_trace(
        Trace(
            kind="agent",
            summary=request.query[:80],
            model=result.model,
            latency_ms=result.latency_ms,
            steps=len(result.steps),
            tools=result.tools_used,
            success=result.completed,
        )
    )
    return ActResponse(
        answer=result.answer,
        steps=[
            ActStep(thought=s.thought, tool=s.tool, args=s.args, observation=s.observation)
            for s in result.steps
        ],
        tools_used=result.tools_used,
        model=result.model,
        latency_ms=result.latency_ms,
        completed=result.completed,
    )
