"""#16 — OpenAI-compatible chat completions for drop-in clients."""

from __future__ import annotations

import json
import time
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from rudra.agents.base import AgentContext, AgentOrchestrator
from rudra.api.deps import require_auth
from rudra.brain.orchestrator import Message
from rudra.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1", tags=["openai-compat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "rudra-jarvis"
    messages: list[ChatMessage]
    stream: bool = False
    agent_type: str | None = None


@router.get("/models")
async def list_models(user_id: str = Depends(require_auth)):
    return {
        "object": "list",
        "data": [
            {"id": "rudra-jarvis", "object": "model", "owned_by": "rudra"},
            {"id": "rudra-executive", "object": "model", "owned_by": "rudra"},
        ],
    }


@router.post("/chat/completions")
async def chat_completions(
    body: ChatCompletionRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    from rudra.agents.types import AgentType
    from rudra.memory.service import MemoryService

    user_msgs = [m for m in body.messages if m.role == "user"]
    query = user_msgs[-1].content if user_msgs else ""
    orch = AgentOrchestrator()
    memory_service = MemoryService(db, user_id)
    ctx = AgentContext(user_id=user_id, session_id="openai-compat")

    if body.agent_type:
        result = await orch.invoke(AgentType(body.agent_type), query, ctx, memory_service=memory_service)
    else:
        result = await orch.route(query, ctx, memory_service=memory_service)

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())

    if body.stream:

        async def gen():
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": body.model,
                "choices": [{"index": 0, "delta": {"content": result.content}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            done = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": body.model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(done)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")

    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "model": body.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": result.content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "rudra_meta": {"agent_type": result.agent_type.value},
    }
