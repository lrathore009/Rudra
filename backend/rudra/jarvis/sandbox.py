"""#14 — Subprocess sandbox for code execution."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from rudra.core.config import get_settings


def run_sandboxed_python(code: str) -> str:
    settings = get_settings()
    timeout = settings.code_exec_timeout_seconds
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        path = Path(f.name)
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={"PATH": "/usr/bin:/bin", "HOME": "/tmp", "PYTHONPATH": ""},
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return out[:8000] if out else f"(exit {proc.returncode})"
    except subprocess.TimeoutExpired:
        return f"Error: execution exceeded {timeout}s"
    finally:
        path.unlink(missing_ok=True)
