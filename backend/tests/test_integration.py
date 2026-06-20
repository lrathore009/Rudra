"""Integration tests covering Rudra's core request paths.

Covers: health endpoints, agent routing, command execution, memory CRUD,
semantic search wiring, and the research engine — with the LLM and embedding
backends stubbed so the suite is fast and deterministic.
"""

from __future__ import annotations

import uuid

import pytest

from rudra.agents.base import AgentContext, AgentOrchestrator, AgentType


# ─── Health ──────────────────────────────────────────────────────────────────
def test_health_endpoint(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "operational"
    assert body["version"]


def test_services_health_endpoint(client):
    resp = client.get("/api/v1/health/services")
    assert resp.status_code == 200
    body = resp.json()
    assert "services" in body and isinstance(body["services"], list)
    names = {s["service"] for s in body["services"]}
    assert {"postgres", "redis", "qdrant", "ollama", "llm"} <= names


def test_list_agents_endpoint(client):
    resp = client.get("/api/v1/agents")
    assert resp.status_code == 200
    agents = resp.json()
    assert len(agents) == 9
    types = {a["type"] for a in agents}
    assert {
        "executive_assistant",
        "research_analyst",
        "concierge",
        "luxury_analyst",
        "travel",
        "knowledge_librarian",
        "writing",
        "presentation",
        "operations",
    } == types
    for agent in agents:
        assert "phase" in agent
        assert agent["phase"]["number"] in range(1, 10)
        assert agent["phase"]["foundation_complete"] is True


# ─── Agent routing ───────────────────────────────────────────────────────────
async def test_auto_route_selects_specialist(stub_llm):
    orch = AgentOrchestrator()
    ctx = AgentContext(user_id="owner", session_id="t")
    resp = await orch.route("Please do deep research on quantum computing", ctx)
    assert resp.agent_type == AgentType.RESEARCH_ANALYST
    assert resp.agent_intro == ""
    assert not resp.content.startswith("I am Rudra's")
    assert "STUB_RESPONSE" in resp.content
    assert len(resp.routing_analysis) >= 1


async def test_invoke_specific_agent(stub_llm):
    orch = AgentOrchestrator()
    ctx = AgentContext(user_id="owner", session_id="t")
    resp = await orch.invoke(AgentType.TRAVEL, "Plan a trip", ctx)
    assert resp.agent_type == AgentType.TRAVEL


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("travel", AgentType.TRAVEL),
        ("The best fit is research_analyst here.", AgentType.RESEARCH_ANALYST),
        ("gibberish-no-match", AgentType.EXECUTIVE_ASSISTANT),
    ],
)
def test_routing_parser_is_robust(raw, expected):
    assert AgentOrchestrator._parse_agent_type(raw) == expected


# ─── Command execution ───────────────────────────────────────────────────────
def test_command_execution(client, stub_llm, stub_embeddings, require_db):
    resp = client.post(
        "/api/v1/command",
        json={"command": "Summarize my day", "auto_route": False},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "STUB_RESPONSE" in body["response"]
    assert not body["response"].startswith("I am Rudra's")
    assert body["agent_intro"] == ""
    assert body["agent_name"] == "Rudra"
    assert body["agent_type"] == "executive_assistant"


# ─── Memory CRUD + semantic search ──────────────────────────────────────────
def test_memory_crud(client, stub_embeddings, require_db):
    # Create
    create = client.post(
        "/api/v1/memories",
        json={
            "memory_type": "semantic",
            "title": "Integration test memory",
            "content": "Rudra stores knowledge with vector embeddings.",
            "tags": ["test"],
        },
    )
    assert create.status_code == 200, create.text
    mem_id = create.json()["id"]

    # Read
    got = client.get(f"/api/v1/memories/{mem_id}")
    assert got.status_code == 200
    assert got.json()["title"] == "Integration test memory"

    # List
    listed = client.get("/api/v1/memories?limit=50")
    assert listed.status_code == 200
    assert any(m["id"] == mem_id for m in listed.json())

    # Delete (hard, to clean up)
    deleted = client.delete(f"/api/v1/memories/{mem_id}?hard=true")
    assert deleted.status_code == 200

    # Confirm gone
    assert client.get(f"/api/v1/memories/{mem_id}").status_code == 404


def test_memory_search_endpoint(client, stub_embeddings, require_db):
    created = client.post(
        "/api/v1/memories",
        json={
            "memory_type": "semantic",
            "title": "Search endpoint target",
            "content": "Notes about espresso machines.",
        },
    )
    assert created.status_code == 200, created.text
    mem_id = created.json()["id"]
    try:
        resp = client.post(
            "/api/v1/memories/search",
            json={"query": "espresso machines", "limit": 5},
        )
        assert resp.status_code == 200, resp.text
        assert isinstance(resp.json(), list)
    finally:
        client.delete(f"/api/v1/memories/{mem_id}?hard=true")


async def test_semantic_search_wiring(stub_embeddings, require_db):
    from rudra.core.database import get_session_factory
    from rudra.memory.models.memory import MemoryType
    from rudra.memory.service import MemoryService

    factory = get_session_factory()
    async with factory() as session:
        svc = MemoryService(session, "test-search-user")
        created = await svc.create(
            MemoryType.SEMANTIC,
            title="Vector search target",
            content="Semantic memory about sailing yachts in Monaco.",
        )
        await session.flush()
        results = await svc.search_by_text("yachts in Monaco", min_similarity=0.0)
        assert isinstance(results, list)
        # The just-created memory (same stubbed vector family) should surface.
        assert any(m.id == created.id for m, _ in results)
        await svc.delete(created.id, hard=True)
        await session.commit()


# ─── Research engine ─────────────────────────────────────────────────────────
async def test_research_with_sources(stub_llm, monkeypatch):
    from rudra.research.engine import ResearchEngine, ResearchSource, SourceType

    async def fake_web(self, query, max_results=10):
        return [
            ResearchSource(
                url="https://reuters.com/x",
                title="Reuters report",
                snippet="Important finding.",
                source_type=SourceType.WEB,
                credibility_score=0.95,
            )
        ]

    async def fake_wiki(self, query, max_results=3):
        return []

    monkeypatch.setattr("rudra.research.engine.WebSearchProvider.search", fake_web)
    monkeypatch.setattr("rudra.research.engine.WikipediaProvider.search", fake_wiki)

    engine = ResearchEngine()
    result = await engine.research("test query", sources=[SourceType.WEB])
    assert result.sources, "expected at least one source"
    assert result.citations and result.citations[0]["url"] == "https://reuters.com/x"
    assert 0.0 < result.confidence_score <= 0.95


async def test_research_graceful_no_sources(stub_llm, monkeypatch):
    from rudra.research.engine import ResearchEngine, SourceType

    async def empty(self, query, max_results=10):
        return []

    monkeypatch.setattr("rudra.research.engine.WebSearchProvider.search", empty)
    monkeypatch.setattr("rudra.research.engine.WikipediaProvider.search", empty)

    engine = ResearchEngine()
    result = await engine.research("obscure query", sources=[SourceType.WEB])
    assert result.sources == []
    assert result.confidence_score == 0.3
    assert result.summary
