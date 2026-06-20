"""Agent routing and context enrichment tests."""

from rudra.agents.base import AgentContext, AgentOrchestrator, AgentType, _heuristic_routing
from rudra.agents.profiles import AGENT_PROFILES


def test_all_agents_have_profiles():
    assert set(AGENT_PROFILES.keys()) == set(AgentType)


def test_heuristic_routing_prefers_travel():
    ranked = _heuristic_routing("Plan a luxury travel itinerary to Tokyo")
    assert ranked[0].agent_type == AgentType.TRAVEL


async def test_route_single_voice_and_analysis(stub_llm):
    orch = AgentOrchestrator()
    ctx = AgentContext(user_id="owner", session_id="t")
    resp = await orch.route("Write a board email about Q3 results", ctx)
    # Single-voice contract: no sub-agent self-introduction reaches the owner.
    assert resp.agent_intro == ""
    assert not resp.content.startswith("I am Rudra's")
    # Internal routing metadata is still recorded for the HUD / details drawer.
    assert resp.agent_name
    assert resp.routing_analysis
    assert any(item["selected"] for item in resp.routing_analysis)
