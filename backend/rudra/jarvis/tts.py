"""#1 — Text-to-speech for spoken Jarvis briefings."""

from __future__ import annotations

import base64
from pathlib import Path

import httpx

from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)


async def synthesize_speech(text: str) -> dict:
    """Return audio bytes (mp3) or browser fallback metadata."""
    settings = get_settings()
    if not settings.enable_jarvis_tts:
        return {"mode": "browser", "text": text}

    if settings.openai_api_key and settings.tts_backend == "openai":
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
            response = await client.audio.speech.create(
                model=settings.tts_openai_model,
                voice=settings.tts_openai_voice,
                input=text[:4096],
            )
            audio = response.content
            cache = Path(settings.data_dir) / "digest_audio.mp3"
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(audio)
            return {
                "mode": "file",
                "path": str(cache),
                "mime": "audio/mpeg",
                "base64": base64.b64encode(audio).decode("ascii"),
            }
        except Exception as e:  # noqa: BLE001
            logger.warning("openai_tts_failed", error=str(e)[:120])

    # Cartesia or other backends can be added; fallback to browser SpeechSynthesis.
    return {"mode": "browser", "text": text, "voice_hints": ["Daniel", "Alex", "en-GB"]}
