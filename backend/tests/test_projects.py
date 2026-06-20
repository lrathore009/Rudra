"""Project OS tests."""

import pytest


def test_project_list(client, require_db):
    res = client.get("/api/v1/projects")
    assert res.status_code == 200
    names = {p["name"] for p in res.json()}
    assert "Rudra OS" in names


def test_project_crud(client, require_db):
    created = client.post(
        "/api/v1/projects",
        json={"name": "Test Venture", "priority": 2, "category": "test"},
    )
    assert created.status_code == 200
    project_id = created.json()["id"]

    patched = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"next_action": "Ship MVP", "status": "active"},
    )
    assert patched.status_code == 200
    assert patched.json()["next_action"] == "Ship MVP"


def test_task_crud(client, require_db):
    projects = client.get("/api/v1/projects").json()
    project = next(p for p in projects if p["name"] == "ChemSphere")
    task = client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Define architecture", "priority": 1},
    )
    assert task.status_code == 200
    task_id = task.json()["id"]
    done = client.patch(
        f"/api/v1/projects/{project['id']}/tasks/{task_id}",
        json={"status": "done"},
    )
    assert done.status_code == 200
    assert done.json()["status"] == "done"


def test_dashboard(client, require_db):
    res = client.get("/api/v1/projects/dashboard")
    assert res.status_code == 200
    body = res.json()
    assert "projects" in body
    assert "weekly_briefing" in body
    assert body["projects"]


@pytest.mark.asyncio
async def test_progress_calculation(require_db):
    from rudra.core.database import get_session_factory
    from rudra.projects.service import ProjectService

    factory = get_session_factory()
    async with factory() as session:
        svc = ProjectService(session, "owner")
        project = await svc.create_project({"name": "Progress Test", "priority": 5})
        await svc.create_task(project.id, {"title": "A", "status": "todo"})
        await svc.create_task(project.id, {"title": "B", "status": "done"})
        progress = await svc.intelligence.calculate_progress(project)
        await session.commit()
        assert progress == 50.0


def test_project_context_in_command(client, require_db, stub_llm, stub_embeddings, monkeypatch):
    captured = {}
    monkeypatch.setenv("COMMAND_USE_REACT_FOR_EA", "false")
    from rudra.core.config import get_settings

    get_settings.cache_clear()

    async def fake_run(self, command, context, user_id, *, agent_type=None):
        captured["context"] = context
        from rudra.agents.base import AgentResponse, AgentType

        return AgentResponse(
            agent_type=AgentType.EXECUTIVE_ASSISTANT,
            content="stub",
            agent_name="Rudra",
            confidence=0.9,
        )

    monkeypatch.setattr("rudra.agents.rudra_command.RudraCommandService.run", fake_run)
    res = client.post(
        "/api/v1/command",
        json={"command": "What should I do next in ChemSphere?", "agent_type": "executive_assistant"},
    )
    assert res.status_code == 200
    assert "project_context" in captured["context"].metadata
