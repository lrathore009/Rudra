"""Agent registry tests."""

from rudra.agents.base import AGENT_REGISTRY, AgentType


def test_all_agents_registered():
    expected = set(AgentType)
    registered = set(AGENT_REGISTRY.keys())
    assert expected == registered


def test_agent_count():
    assert len(AGENT_REGISTRY) == 9
