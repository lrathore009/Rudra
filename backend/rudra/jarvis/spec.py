"""#12 — Declarative Rudra spec (TOML) overlay on env config."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rudra.core.config import _REPO_ROOT, get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)

_SPEC_PATH = _REPO_ROOT / "configs" / "rudra.toml"


def load_spec() -> dict[str, Any]:
    path = Path(get_settings().rudra_spec_path or _SPEC_PATH)
    if not path.exists():
        return {}
    try:
        import tomllib

        with path.open("rb") as f:
            data = tomllib.load(f)
        logger.info("rudra_spec_loaded", path=str(path))
        return data if isinstance(data, dict) else {}
    except Exception as e:  # noqa: BLE001
        logger.warning("rudra_spec_load_failed", error=str(e)[:120])
        return {}


def spec_section(name: str) -> dict[str, Any]:
    spec = load_spec()
    section = spec.get(name, {})
    return section if isinstance(section, dict) else {}


def effective_jarvis_config() -> dict[str, Any]:
    """Merge env settings with TOML [jarvis] section."""
    settings = get_settings()
    jarvis = spec_section("jarvis")
    return {
        "persona": jarvis.get("persona", settings.jarvis_persona),
        "honorific": jarvis.get("honorific", settings.jarvis_honorific),
        "digest_schedule": jarvis.get("digest_schedule", settings.morning_digest_time),
        "tts_backend": jarvis.get("tts_backend", settings.tts_backend),
        "operators_enabled": jarvis.get("operators_enabled", settings.enable_operators),
        "minions_routing": jarvis.get("minions_routing", settings.enable_minions_routing),
    }
