"""P1 — ReAct loop tests with a scripted (offline) brain."""

from rudra.agents.react import ReActAgent
from rudra.agents.tools import ToolContext, build_default_registry
from rudra.brain.orchestrator import CompletionResult, ModelProvider


class _ScriptedBrain:
    """Returns a fixed sequence of model outputs, simulating a tool-using model."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    async def think(self, messages, *, system=None, model_tier="default"):
        content = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return CompletionResult(content=content, provider=ModelProvider.OLLAMA, model_id="stub")


def _registry():
    return build_default_registry(include_code=False)


async def test_react_uses_tool_then_answers():
    brain = _ScriptedBrain(
        [
            'Thought: I should compute it.\nAction: {"tool": "calculator", "args": {"expression": "6*7"}}',
            "Thought: Done.\nFinal Answer: The answer is 42.",
        ]
    )
    agent = ReActAgent(brain=brain, registry=_registry(), max_steps=4)
    result = await agent.run("What is 6*7?", ToolContext())

    assert result.completed is True
    assert "42" in result.answer
    assert "calculator" in result.tools_used
    # one tool step + one final-answer step
    assert len(result.steps) == 2
    assert result.steps[0].tool == "calculator"
    assert result.steps[0].observation == "42"


async def test_react_plain_text_is_treated_as_answer():
    brain = _ScriptedBrain(["Here is my direct answer with no tool call."])
    agent = ReActAgent(brain=brain, registry=_registry(), max_steps=3)
    result = await agent.run("hello", ToolContext())
    assert result.completed is True
    assert "direct answer" in result.answer.lower()
    assert result.tools_used == []


async def test_react_respects_max_steps():
    # Always emits an action, never a final answer -> must stop at max_steps + 1 synthesis.
    looping = 'Thought: keep going.\nAction: {"tool": "current_time", "args": {}}'
    brain = _ScriptedBrain([looping] * 10)
    agent = ReActAgent(brain=brain, registry=_registry(), max_steps=2)
    result = await agent.run("loop forever", ToolContext())
    assert result.completed is False
    assert len(result.steps) == 2
