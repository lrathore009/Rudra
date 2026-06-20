"""Streaming command (SSE) — tokens stream incrementally and stay single-voice."""

import json


def test_command_stream_emits_tokens(client, monkeypatch, stub_embeddings, require_db):
    async def fake_stream(self, messages, *, system=None, model_tier="default"):
        for tok in ["Hello", " ", "owner", "."]:
            yield tok

    monkeypatch.setattr("rudra.brain.orchestrator.Brain.stream_think", fake_stream)

    with client.stream(
        "POST",
        "/api/v1/command/stream",
        json={"command": "what's on my calendar today", "auto_route": True},
    ) as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")
        raw = "".join(resp.iter_text())

    events = [json.loads(ln[5:].strip()) for ln in raw.splitlines() if ln.startswith("data:")]
    types = [e["type"] for e in events]
    assert types[0] == "meta"
    assert "token" in types
    assert types[-1] == "done"

    tokens = "".join(e["text"] for e in events if e["type"] == "token")
    assert "Hello owner." in tokens

    done = next(e for e in events if e["type"] == "done")
    assert done["agent_name"] == "Rudra"
