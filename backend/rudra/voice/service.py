"""Voice layer — STT/TTS foundation for hands-free Jarvis (#7)."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from enum import Enum

from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)


class VoiceState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


@dataclass
class VoiceSession:
    session_id: str
    state: VoiceState = VoiceState.IDLE
    wake_word_detected: bool = False
    transcript: str = ""


class VoiceService:
    WAKE_WORD = "rudra"

    def __init__(self):
        self._sessions: dict[str, VoiceSession] = {}

    def is_enabled(self) -> bool:
        return get_settings().enable_voice or get_settings().enable_jarvis_tts

    def _session(self, session_id: str) -> VoiceSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = VoiceSession(session_id=session_id)
        return self._sessions[session_id]

    async def process_audio(self, session_id: str, audio_data: bytes) -> dict:
        settings = get_settings()
        sess = self._session(session_id)
        sess.state = VoiceState.PROCESSING
        if not audio_data:
            return {
                "status": "ready",
                "wake_word": settings.wake_word,
                "hint": "Send audio bytes or use browser SpeechRecognition",
            }
        if settings.stt_backend == "openai" and settings.openai_api_key:
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
                # Whisper API expects a file-like object
                from io import BytesIO

                bio = BytesIO(audio_data)
                bio.name = "audio.webm"
                tr = await client.audio.transcriptions.create(model="whisper-1", file=bio)
                sess.transcript = tr.text
                sess.state = VoiceState.IDLE
                lowered = tr.text.lower()
                trigger = (
                    settings.wake_word.lower() in lowered
                    or "good morning" in lowered
                    or "morning digest" in lowered
                )
                return {
                    "status": "ok",
                    "transcript": tr.text,
                    "trigger_digest": "good morning" in lowered or "morning digest" in lowered,
                    "wake_detected": trigger,
                }
            except Exception as e:  # noqa: BLE001
                logger.warning("whisper_failed", error=str(e)[:120])
        return {
            "status": "browser_fallback",
            "message": "Use browser SpeechRecognition or set OPENAI_API_KEY for Whisper STT",
            "audio_b64_len": len(base64.b64encode(audio_data)) if audio_data else 0,
        }
