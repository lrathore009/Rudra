"""#5 — skill.toml pipeline execution (OpenJarvis-style structured skills)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from rudra.core.logging import get_logger

logger = get_logger(__name__)


def load_skill_toml(skill_dir: Path) -> dict[str, Any] | None:
    path = skill_dir / "skill.toml"
    if not path.exists():
        return None
    try:
        import tomllib

        with path.open("rb") as f:
            data = tomllib.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def skill_catalog_xml(skills: list[dict[str, str]]) -> str:
    lines = ["<available_skills>"]
    for s in skills:
        lines.append(f'  <skill name="{s["name"]}" description="{s["description"][:120]}" />')
    lines.append("</available_skills>")
    return "\n".join(lines)


async def run_pipeline_skill(
    skill_dir: Path,
    args: dict[str, Any],
    *,
    tool_executor,
) -> str:
    """Execute [[skill.steps]] from skill.toml via injected tool_executor(name, args)->str."""
    spec = load_skill_toml(skill_dir)
    if not spec or "skill" not in spec:
        return "No pipeline defined in skill.toml"
    steps = spec.get("skill", {}).get("steps") or spec.get("steps") or []
    if not isinstance(steps, list):
        return "Invalid skill steps"
    context = dict(args)
    outputs: list[str] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        template = step.get("arguments_template") or step.get("args_template") or "{}"
        rendered = template
        for key, val in context.items():
            rendered = rendered.replace("{" + key + "}", str(val))
        try:
            parsed_args = json.loads(rendered)
        except json.JSONDecodeError:
            parsed_args = {}
        tool_name = step.get("tool_name")
        if tool_name:
            obs = await tool_executor(tool_name, parsed_args)
            outputs.append(obs)
            out_key = step.get("output_key")
            if out_key:
                context[out_key] = obs
    return "\n---\n".join(outputs) if outputs else "Pipeline produced no output"
