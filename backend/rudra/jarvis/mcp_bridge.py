"""#10 — MCP tool bridge (stdio servers from config)."""

from __future__ import annotations

import json
import subprocess
from typing import Any

from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)


def list_mcp_servers() -> list[dict[str, str]]:
    raw = get_settings().mcp_servers_json
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [s for s in data if isinstance(s, dict)]
    except Exception:
        pass
    return []


async def call_mcp_tool(server_name: str, tool_name: str, arguments: dict[str, Any]) -> str:
    """Best-effort MCP invoke via configured stdio command (single-shot JSON-RPC)."""
    servers = {s.get("name", ""): s for s in list_mcp_servers()}
    cfg = servers.get(server_name)
    if not cfg:
        return f"Unknown MCP server '{server_name}'. Configured: {list(servers)}"
    cmd = cfg.get("command")
    if not cmd:
        return f"MCP server '{server_name}' has no command"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    try:
        proc = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            input=json.dumps(payload).encode(),
            capture_output=True,
            timeout=30,
            check=False,
        )
        return proc.stdout.decode()[:4000] or proc.stderr.decode()[:500]
    except Exception as e:  # noqa: BLE001
        logger.warning("mcp_call_failed", server=server_name, error=str(e)[:120])
        return f"MCP call failed: {e}"
