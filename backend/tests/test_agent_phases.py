"""Agent phase registry tests."""

from rudra.agents.base import AGENT_REGISTRY
from rudra.agents.phases import AGENT_PHASES, PhaseStatus, phase_for, phase_to_dict
from rudra.agents.types import AgentType


def test_all_agents_have_phases():
    assert set(AGENT_PHASES.keys()) == set(AgentType)
    assert set(AGENT_PHASES.keys()) == set(AGENT_REGISTRY.keys())


def test_phase_numbers_are_one_through_nine():
    numbers = sorted(p.number for p in AGENT_PHASES.values())
    assert numbers == list(range(1, 10))


def test_phase_titles_are_unique():
    titles = [p.title for p in AGENT_PHASES.values()]
    assert len(titles) == len(set(titles))


def test_all_phases_complete():
    for agent_type in AgentType:
        phase = phase_for(agent_type)
        assert phase.status == PhaseStatus.COMPLETE


def test_build_registry_includes_phase_tools():
    from rudra.agents.tools import build_registry_for_agent

    reg = build_registry_for_agent(AgentType.EXECUTIVE_ASSISTANT)
    names = reg.names()
    assert "get_daily_briefing" in names
    assert "list_active_projects" in names


def test_phase_to_dict_includes_required_fields():
    data = phase_to_dict(AgentType.EXECUTIVE_ASSISTANT)
    assert data["number"] == 1
    assert data["title"] == "Executive Command Center"
    assert data["status"] == "complete"
    assert data["foundation_complete"] is True
    assert data["tools"]
    assert data["deliverables"]
    assert data["depends_on"]
