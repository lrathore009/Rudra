"""Free, local-first embedding pipeline.

Generates 768-dimensional vectors using (in order of preference):
  1. Ollama  — nomic-embed-text  (fully local, $0, private)
  2. Gemini  — text-embedding-004 (free tier, $0)
  3. OpenAI  — text-embedding-3-small (paid, only if key set)

All failures are non-fatal: memories are still stored without a vector so the
system degrades gracefully and never blocks on embeddings.
"""

from __future__ import annotations

import httpx

from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.dim = self.settings.embedding_dim

    async def embed(self, text: str) -> list[float] | None:
        if not text or not text.strip():
            return None

        provider = self.settings.embedding_provider
        order = (
            ["ollama", "gemini", "openai"]
            if provider == "auto"
            else [provider]
        )

        for name in order:
            try:
                if name == "ollama":
                    vec = await self._ollama(text)
                elif name == "gemini" and self.settings.google_ai_api_key:
                    vec = await self._gemini(text)
                elif name == "openai" and self.settings.openai_api_key:
                    vec = await self._openai(text)
                else:
                    continue
                if vec:
                    return vec
            except Exception as e:  # noqa: BLE001
                logger.warning("embedding_provider_failed", provider=name, error=str(e)[:120])
                continue

        logger.info("embedding_unavailable", note="stored without vector")
        return None

    async def _ollama(self, text: str) -> list[float] | None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.settings.ollama_base_url}/api/embeddings",
                json={"model": self.settings.embedding_model_ollama, "prompt": text},
            )
            resp.raise_for_status()
            return resp.json().get("embedding")

    async def _gemini(self, text: str) -> list[float] | None:
        import google.generativeai as genai

        genai.configure(api_key=self.settings.google_ai_api_key.get_secret_value())
        result = genai.embed_content(
            model=self.settings.embedding_model_gemini, content=text
        )
        return result["embedding"]

    async def _openai(self, text: str) -> list[float] | None:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.settings.openai_api_key.get_secret_value())
        resp = await client.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding


_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service


async def embed_text(text: str) -> list[float] | None:
    return await get_embedding_service().embed(text)
