"""P4 — CodeAct: a gated Python execution tool.

SAFETY: this runs model-authored code. It is DISABLED by default
(``ENABLE_CODE_EXECUTION=false``). A subprocess + timeout + Python isolated mode is a
pragmatic guard, NOT a real sandbox — for production use a container / microVM / seccomp.
Never enable in a multi-user or internet-exposed deployment without proper isolation.
"""

from __future__ import annotations

import asyncio
import sys
import time

from rudra.agents.tools import Tool, ToolContext
from rudra.core.config import get_settings
from rudra.core.logging import get_logger
from rudra.jarvis.sandbox import run_sandboxed_python

logger = get_logger(__name__)


async def _run_python(args: dict, ctx: ToolContext) -> str:
    settings = get_settings()
    if not settings.enable_code_execution:
        return (
            "Code execution is disabled. Set ENABLE_CODE_EXECUTION=true to enable it "
            "(only in a trusted, isolated environment)."
        )
    code = str(args.get("code", "")).strip()
    if not code:
        return "Error: provide 'code' (Python source)."

    if settings.use_sandbox_code_exec:
        return run_sandboxed_python(code)

    timeout = settings.code_exec_timeout_seconds
    try:
        # -I = isolated mode: ignore env vars and user site-packages.
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-I",
            "-c",
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except Exception as e:  # noqa: BLE001
        return f"Error launching interpreter: {e}"

    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return f"Error: code timed out after {timeout}s."

    text = (out or b"").decode("utf-8", "replace")[:4000]
    return text or "(no output)"


def code_exec_tool() -> Tool:
    return Tool(
        name="run_python",
        description="Execute a short Python snippet and return its stdout (gated; timeout-sandboxed).",
        parameters={"code": "Python source to run"},
        handler=_run_python,
        safe=False,
    )
