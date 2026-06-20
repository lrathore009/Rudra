"""P1 — ReAct agent: a model-agnostic think -> act -> observe loop.

Turns Rudra's one-shot agents into multi-step, tool-using agents. The protocol is
prompt-based (works with any Ollama/cloud model): each turn the model emits either an
Action (a JSON tool call) or a Final Answer. Guardrails: a tool allowlist (only tools in
the registry are callable), a max-steps cap, and unsafe tools (e.g. code execution) that
exist in the registry only when explicitly enabled in config.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

from rudra.agents.tools import ToolContext, ToolRegistry, build_default_registry
from rudra.brain.orchestrator import Brain, Message
from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)

REACT_SYSTEM = """You are Rudra's autonomous agent. You accomplish the owner's task by reasoning step by step and using tools.

Available tools:
{tools}

On EACH turn reply in EXACTLY one of these two formats and nothing else:

Thought: <your reasoning>
Action: {{"tool": "<tool_name>", "args": {{...}}}}

— or, once you have enough information —

Thought: <your reasoning>
Final Answer: <the complete answer for the owner>

Rules:
- One Action per turn. After an Action you will be given an Observation, then continue.
- Prefer tools over guessing for facts, math, the current time, or the owner's memory.
- Never fabricate an Observation. Give a Final Answer as soon as you can.
"""

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> dict | None:
    match = _JSON_RE.search(text)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


@dataclass
class ReActStep:
    thought: str
    tool: str | None = None
    args: dict[str, Any] = field(default_factory=dict)
    observation: str | None = None


@dataclass
class ReActResult:
    answer: str
    steps: list[ReActStep]
    tools_used: list[str]
    model: str
    latency_ms: int
    completed: bool


class ReActAgent:
    """A tool-using agent that loops until it produces a Final Answer or runs out of steps."""

    def __init__(
        self,
        brain: Brain | None = None,
        registry: ToolRegistry | None = None,
        *,
        max_steps: int | None = None,
    ) -> None:
        self.brain = brain or Brain()
        self.registry = registry or build_default_registry()
        self.max_steps = max_steps or get_settings().agent_max_steps

    async def run(self, query: str, ctx: ToolContext | None = None) -> ReActResult:
        ctx = ctx or ToolContext()
        system = REACT_SYSTEM.format(tools=self.registry.describe_for_prompt())
        transcript = f"Task: {query}\n"
        steps: list[ReActStep] = []
        tools_used: list[str] = []
        model_id = "unknown"
        started = time.time()

        for _ in range(self.max_steps):
            result = await self.brain.think([Message(role="user", content=transcript)], system=system)
            model_id = result.model_id
            text = result.content.strip()
            lowered = text.lower()

            if "final answer:" in lowered:
                idx = lowered.index("final answer:")
                answer = text[idx + len("final answer:") :].strip()
                thought = text[:idx].replace("Thought:", "").strip()
                steps.append(ReActStep(thought=thought))
                return self._result(answer, steps, tools_used, model_id, started, True)

            payload = _extract_json(text)
            thought = re.split(r"Action:", text, maxsplit=1)[0].replace("Thought:", "").strip()

            if not payload or "tool" not in payload:
                # Model ignored the protocol — treat its text as the final answer.
                steps.append(ReActStep(thought=thought or text))
                return self._result(text, steps, tools_used, model_id, started, True)

            tool_name = str(payload.get("tool", ""))
            args = payload.get("args") or {}
            if not isinstance(args, dict):
                args = {}

            observation = await self.registry.execute(tool_name, args, ctx)
            tools_used.append(tool_name)
            steps.append(
                ReActStep(thought=thought, tool=tool_name, args=args, observation=observation)
            )
            transcript += (
                f"\nThought: {thought}\nAction: {json.dumps(payload)}\nObservation: {observation}\n"
            )

        # Out of steps — request a best-effort synthesis.
        result = await self.brain.think(
            [
                Message(
                    role="user",
                    content=transcript + "\nYou have used all your steps. Give your best Final Answer now.",
                )
            ],
            system=system,
        )
        final = result.content.strip()
        low = final.lower()
        if "final answer:" in low:
            final = final[low.index("final answer:") + len("final answer:") :].strip()
        return self._result(final, steps, tools_used, result.model_id, started, False)

    @staticmethod
    def _result(answer, steps, tools_used, model_id, started, completed) -> ReActResult:
        return ReActResult(
            answer=answer,
            steps=steps,
            tools_used=tools_used,
            model=model_id,
            latency_ms=int((time.time() - started) * 1000),
            completed=completed,
        )
