"""Jarvis supreme-assistant layer tests."""

from rudra.jarvis.events import EventType, get_event_bus
from rudra.jarvis.guardrails import scan_and_redact
from rudra.jarvis.learning import routing_hints_from_traces, suggest_agent_for_query
from rudra.jarvis.minions import classify_complexity
from rudra.jarvis.persona import jarvis_system_prompt
from rudra.jarvis.spec import effective_jarvis_config
from rudra.jarvis.telemetry import estimate_cost, estimate_energy_wh
from rudra.skills.pipeline import skill_catalog_xml


def test_jarvis_persona_includes_honorific():
    prompt = jarvis_system_prompt(mode="digest")
    assert "sir" in prompt.lower() or "chief of staff" in prompt.lower()


def test_guardrails_redact_email():
    result = scan_and_redact("Contact me at owner@example.com please")
    assert "REDACTED" in result.redacted_text
    assert "email" in result.findings


def test_minions_complexity():
    assert classify_complexity("What is on my calendar?") == "local"
    assert classify_complexity("Do deep research and compare market strategy") == "cloud"


def test_telemetry_estimates():
    assert estimate_cost("gpt-4o", 1000, 500) >= 0
    assert estimate_energy_wh(5000, local=True) >= 0


def test_event_bus_publish():
    bus = get_event_bus()
    seen: list[str] = []
    bus.subscribe(EventType.BRIEFING_GENERATED, lambda t, p: seen.append(t.value))
    bus.publish(EventType.BRIEFING_GENERATED, {"test": True})
    assert seen == ["briefing_generated"]


def test_routing_hints_empty_ok():
    hints = routing_hints_from_traces(limit=10)
    assert "trace_count" in hints


def test_suggest_agent_briefing():
    assert suggest_agent_for_query("prepare my daily briefing") == "executive_assistant"


def test_skill_catalog_xml():
    xml = skill_catalog_xml([{"name": "test-skill", "description": "A test"}])
    assert "available_skills" in xml
    assert "test-skill" in xml


def test_effective_jarvis_config():
    cfg = effective_jarvis_config()
    assert "honorific" in cfg
    assert "tts_backend" in cfg
