"""Integration foundation tests."""

import pytest


def test_integrations_list_connectors(client, require_db):
    res = client.get("/api/v1/integrations")
    assert res.status_code == 200
    providers = {i["provider"] for i in res.json()}
    assert "google" in providers
    assert "notion" in providers
    assert "mock_local" in providers


def test_connect_mock_calendar_and_email(client, require_db):
    connect = client.post("/api/v1/integrations/connect/mock")
    assert connect.status_code == 200
    events = client.get("/api/v1/calendar/events")
    assert events.status_code == 200
    assert len(events.json()) >= 1
    emails = client.get("/api/v1/email/recent")
    assert emails.status_code == 200
    assert len(emails.json()) >= 1


def test_command_stack(client, require_db):
    client.post("/api/v1/integrations/connect/mock")
    res = client.get("/api/v1/integrations/command-stack")
    assert res.status_code == 200
    body = res.json()
    assert "tier1" in body
    assert "tier2" in body
    assert "commitments" in body
    assert body["tier1"]["calendar"]


def test_sync_integrations(client, require_db):
    client.post("/api/v1/integrations/connect/mock")
    res = client.post("/api/v1/integrations/sync")
    assert res.status_code == 200
    assert res.json().get("calendar", 0) >= 1


def test_csv_import_finance(client, require_db):
    csv_text = "label,amount,currency,category\nOperating cash,100000,USD,cash\n"
    res = client.post(
        "/api/v1/integrations/import/csv",
        json={"kind": "finance", "csv_text": csv_text},
    )
    assert res.status_code == 200
    assert res.json()["imported"] == 1


def test_daily_briefing(client, require_db):
    client.post("/api/v1/integrations/connect/mock")
    res = client.post("/api/v1/briefing/daily")
    assert res.status_code == 200
    body = res.json()
    assert "briefing_date" in body
    assert "Daily Command Briefing" in body["content"]
    assert "Project focus" in body["content"]


@pytest.mark.asyncio
async def test_scheduler_briefing_job(require_db):
    from rudra.autonomy.scheduler import morning_digest

    result = await morning_digest()
    assert "Daily Command Briefing" in result
