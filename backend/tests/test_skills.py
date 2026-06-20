"""P2 — SKILL.md loader tests (progressive disclosure)."""

from rudra.skills.loader import SkillRegistry


def _write_skill(root, folder, name, description, body):
    d = root / folder
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n{body}\n", encoding="utf-8"
    )


def test_discovery_and_activation(tmp_path):
    skills_dir = tmp_path / "skills"
    _write_skill(skills_dir, "demo", "demo", "A demo skill.", "# Demo\nDo the thing.")

    reg = SkillRegistry(skills_dir=skills_dir)

    # Discovery: name + description only.
    assert reg.list() == [{"name": "demo", "description": "A demo skill."}]

    # Activation: full body, frontmatter stripped.
    skill = reg.get("demo")
    assert skill is not None
    body = skill.load_body()
    assert "Do the thing." in body
    assert "description:" not in body


def test_empty_dir_is_safe(tmp_path):
    reg = SkillRegistry(skills_dir=tmp_path / "nonexistent")
    assert reg.list() == []
    assert reg.get("anything") is None


def test_bundled_skills_present():
    """The repo ships at least the two reference skills via the default settings dir."""
    reg = SkillRegistry()
    names = {s["name"] for s in reg.list()}
    assert {"web-research", "daily-briefing"} <= names
