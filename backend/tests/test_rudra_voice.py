"""Single-voice (Rudra) contract — no sub-agent self-introduction reaches the owner."""

from rudra.agents.base import AGENT_REGISTRY, OPERATING_PRINCIPLES, AgentContext, AgentOrchestrator
from rudra.brain.orchestrator import Brain


def test_format_response_strips_intro():
    brain = Brain()
    for cls in AGENT_REGISTRY.values():
        agent = cls(brain)
        intro, content = agent.format_response("Here is the answer.")
        assert intro == ""
        assert content == "Here is the answer."
        assert "I am Rudra" not in content


def test_operating_principles_enforce_single_voice():
    assert "ONE voice" in OPERATING_PRINCIPLES
    assert "Never introduce yourself" in OPERATING_PRINCIPLES


async def test_route_content_has_no_intro(stub_llm):
    orch = AgentOrchestrator()
    resp = await orch.route(
        "Plan a trip to Tokyo", AgentContext(user_id="owner", session_id="t")
    )
    assert resp.agent_intro == ""
    assert not resp.content.lower().startswith("i am rudra")
