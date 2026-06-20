"""Knowledge graph tests."""

import pytest
from sqlalchemy import select

from rudra.graph.extraction import extract_entities_rule_based
from rudra.graph.models import Entity, GraphRelationship, MemoryEntityLink
from rudra.graph.service import GraphService
from rudra.memory.models.memory import MemoryType
from rudra.memory.service import MemoryService


def test_entity_extraction_rule_based():
    text = "Vikram Rathore is building Rudra OS and Jobsflix Nexus AI."
    found = extract_entities_rule_based(text)
    names = {e.name for e in found}
    assert "Vikram Rathore" in names
    assert "Rudra OS" in names
    assert "Jobsflix Nexus AI" in names


@pytest.mark.asyncio
async def test_entity_creation(require_db):
    from rudra.core.database import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        graph = GraphService(session, "owner")
        entity = await graph.get_or_create_entity("ChemSphere", "project")
        await session.commit()
        assert entity.name == "ChemSphere"
        assert entity.entity_type == "project"


@pytest.mark.asyncio
async def test_relationship_creation(require_db):
    from rudra.core.database import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        graph = GraphService(session, "owner")
        a = await graph.get_or_create_entity("Vikram Rathore", "person")
        b = await graph.get_or_create_entity("ChemSphere", "project")
        rel = await graph.create_relationship(a.id, b.id, "works_on")
        await session.commit()
        assert rel.relation_type == "works_on"


@pytest.mark.asyncio
async def test_memory_entity_linking(require_db, stub_embeddings):
    from rudra.core.database import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        memory = await MemoryService(session, "owner").create(
            MemoryType.EPISODIC,
            "ChemSphere update",
            "Progress on ChemSphere with Vikram Rathore leading the build.",
        )
        linked = await GraphService(session, "owner").extract_and_link_memory(memory)
        await session.commit()
        assert len(linked) >= 1
        result = await session.execute(select(MemoryEntityLink))
        assert result.scalars().first() is not None


def test_graph_list_entities(client, require_db):
    res = client.get("/api/v1/graph/entities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert any(e["name"] == "Rudra OS" for e in data)


def test_graph_entity_detail(client, require_db):
    listing = client.get("/api/v1/graph/entities?q=Rudra")
    assert listing.status_code == 200
    entities = listing.json()
    assert entities
    entity_id = entities[0]["id"]
    detail = client.get(f"/api/v1/graph/entities/{entity_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == entity_id


def test_graph_relationships_api(client, require_db):
    entities = client.get("/api/v1/graph/entities").json()
    by_name = {e["name"]: e for e in entities}
    source = by_name.get("Vikram Rathore")
    target = by_name.get("Rudra OS")
    assert source and target
    res = client.post(
        "/api/v1/graph/relationships",
        json={
            "source_entity_id": source["id"],
            "target_entity_id": target["id"],
            "relation_type": "owns",
        },
    )
    assert res.status_code == 200
    listed = client.get("/api/v1/graph/relationships")
    assert listed.status_code == 200
    assert len(listed.json()) >= 1
