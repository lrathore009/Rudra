"""P2 — Agent Skills API (SKILL.md open standard)."""

from fastapi import APIRouter, HTTPException

from rudra.skills.loader import get_skill_registry

router = APIRouter()


@router.get("/skills")
async def list_skills():
    """Discovery: list installed skills (name + description only)."""
    return get_skill_registry().list()


@router.post("/skills/reload")
async def reload_skills():
    reg = get_skill_registry()
    reg.reload()
    return {"reloaded": True, "count": len(reg.list())}


@router.get("/skills/{name}")
async def get_skill(name: str):
    """Activation: load a skill's full instructions."""
    skill = get_skill_registry().get(name)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")
    return {"name": skill.name, "description": skill.description, "instructions": skill.load_body()}
