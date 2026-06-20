"""Phase 2 — RudraCommandService single-voice orchestration."""

from rudra.agents.base import AGENT_REGISTRY, AgentContext
from rudra.agents.rudra_command import RUDRA_PERSONA, RudraCommandService
from rudra.agents.types import AgentType


def test_classify_fast_is_instant_and_complete():
    svc = RudraCommandService()
    agent_type, candidates = svc.classify_fast("Plan a luxury trip to Tokyo")
    assert agent_type == AgentType.TRAVEL
    assert len(candidates) == len(AgentType)


def test_rudra_system_is_single_voice():
    svc = RudraCommandService()
    agent = AGENT_REGISTRY[AgentType.RESEARCH_ANALYST](svc.brain)
    system = svc.rudra_system(agent, "## Intel\n- something")
    assert "You ARE Rudra" in system
    assert "never reveal" in system.lower()
    assert "## Intel" in system  # enriched block is included


def test_persona_forbids_self_intro():
    assert "ALWAYS speak as ONE assistant" in RUDRA_PERSONA
    assert "NEVER say" in RUDRA_PERSONA


async def test_run_returns_single_rudra_voice(stub_llm, monkeypatch):
    # Isolate synthesis from enrichment (enrichment is integration-tested elsewhere).
    async def fake_enrich(self, query, agent_type, context, user_id):
        return "SYSTEM", [{"type": "memory", "title": "x"}], context

    monkeypatch.setattr(
        "rudra.agents.rudra_command.RudraCommandService.enrich_and_build", fake_enrich
    )
    svc = RudraCommandService()
    resp = await svc.run(
        "Research quantum computing",
        AgentContext(user_id="owner", session_id="t"),
        "owner",
        agent_type=AgentType.RESEARCH_ANALYST,
    )
    assert resp.agent_name == "Rudra"
    assert resp.agent_intro == ""
    assert not resp.content.startswith("I am Rudra's")
    assert "STUB_RESPONSE" in resp.content
    assert resp.voice_profile.get("rate")  # one consistent Rudra voice
    assert any(item["selected"] for item in resp.routing_analysis)
