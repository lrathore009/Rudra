"""P2 — Agent Skills loader (agentskills.io / Anthropic SKILL.md open standard).

A *skill* is a folder containing a ``SKILL.md`` with YAML frontmatter (``name``,
``description``) plus markdown instructions, optionally bundling scripts/references.
Progressive disclosure: discovery (name + description) -> activation (full body) ->
execution. The agent reaches skills through the ``use_skill`` tool (see agents/tools.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)


def _split_frontmatter(md: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Tolerant of missing/invalid frontmatter."""
    if md.startswith("---"):
        parts = md.split("---", 2)
        if len(parts) == 3:
            try:
                data = yaml.safe_load(parts[1]) or {}
            except Exception:  # noqa: BLE001
                data = {}
            return (data if isinstance(data, dict) else {}), parts[2].strip()
    return {}, md.strip()


@dataclass
class Skill:
    name: str
    description: str
    path: Path

    def load_body(self) -> str:
        md = (self.path / "SKILL.md").read_text(encoding="utf-8")
        _, body = _split_frontmatter(md)
        return body


class SkillRegistry:
    def __init__(self, skills_dir: str | Path | None = None) -> None:
        self.skills_dir = Path(skills_dir or get_settings().skills_dir)
        self._skills: dict[str, Skill] = {}
        self.reload()

    def reload(self) -> None:
        self._skills.clear()
        if not self.skills_dir.exists():
            return
        for skill_md in sorted(self.skills_dir.glob("*/SKILL.md")):
            try:
                fm, _ = _split_frontmatter(skill_md.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            name = str(fm.get("name") or skill_md.parent.name)
            self._skills[name] = Skill(
                name=name,
                description=str(fm.get("description") or ""),
                path=skill_md.parent,
            )
        logger.info("skills_loaded", count=len(self._skills), dir=str(self.skills_dir))

    def list(self) -> list[dict[str, str]]:
        return [{"name": s.name, "description": s.description} for s in self._skills.values()]

    def catalog_xml(self) -> str:
        from rudra.skills.pipeline import skill_catalog_xml

        return skill_catalog_xml(self.list())

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)


_registry: SkillRegistry | None = None


def get_skill_registry() -> SkillRegistry:
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry
