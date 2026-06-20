"""Brain layer — central orchestrator for multi-model intelligence."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator

import httpx
import time
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from rudra.core.config import get_settings
from rudra.core.logging import get_logger

logger = get_logger(__name__)


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"


@dataclass
class ModelConfig:
    provider: ModelProvider
    model_id: str
    max_tokens: int = 4096
    temperature: float = 0.7
    priority: int = 0  # lower = preferred


@dataclass
class Message:
    role: str
    content: str


@dataclass
class CompletionResult:
    content: str
    provider: ModelProvider
    model_id: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"


# Sentinel: the Ollama model id is resolved at runtime from settings.ollama_chat_model
# (never hardcoded here), so the local model is fully environment-driven.
_OLLAMA = ""

# Fallback order (graceful): Gemini → OpenAI → Anthropic → Ollama.
# Cloud providers are tried first when their keys exist; Ollama is the always-available
# local safety net. With no cloud keys configured, only Ollama runs (free, private).
DEFAULT_MODELS: list[ModelConfig] = [
    ModelConfig(ModelProvider.GOOGLE, "gemini-2.0-flash", priority=0),
    ModelConfig(ModelProvider.OPENAI, "gpt-4o", priority=1),
    ModelConfig(ModelProvider.ANTHROPIC, "claude-sonnet-4-20250514", priority=2),
    ModelConfig(ModelProvider.OLLAMA, _OLLAMA, priority=3),
]

REASONING_MODELS: list[ModelConfig] = [
    ModelConfig(ModelProvider.GOOGLE, "gemini-2.0-flash", priority=0),
    ModelConfig(ModelProvider.OPENAI, "o1", priority=1),
    ModelConfig(ModelProvider.ANTHROPIC, "claude-sonnet-4-20250514", priority=2),
    ModelConfig(ModelProvider.OLLAMA, _OLLAMA, priority=3),
]

FAST_MODELS: list[ModelConfig] = [
    ModelConfig(ModelProvider.GOOGLE, "gemini-1.5-flash", priority=0),
    ModelConfig(ModelProvider.OPENAI, "gpt-4o-mini", priority=1),
    ModelConfig(ModelProvider.ANTHROPIC, "claude-3-5-haiku-20241022", priority=2),
    ModelConfig(ModelProvider.OLLAMA, _OLLAMA, priority=3),
]


class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        config: ModelConfig,
        *,
        system: str | None = None,
    ) -> CompletionResult:
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        config: ModelConfig,
        *,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        key = settings.openai_api_key
        self.client = AsyncOpenAI(api_key=key.get_secret_value() if key else None)

    async def complete(
        self, messages: list[Message], config: ModelConfig, *, system: str | None = None
    ) -> CompletionResult:
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        if system:
            msgs.insert(0, {"role": "system", "content": system})

        response = await self.client.chat.completions.create(
            model=config.model_id,
            messages=msgs,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
        choice = response.choices[0]
        return CompletionResult(
            content=choice.message.content or "",
            provider=ModelProvider.OPENAI,
            model_id=config.model_id,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            },
            finish_reason=choice.finish_reason or "stop",
        )

    async def stream(
        self, messages: list[Message], config: ModelConfig, *, system: str | None = None
    ) -> AsyncIterator[str]:
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        if system:
            msgs.insert(0, {"role": "system", "content": system})

        stream = await self.client.chat.completions.create(
            model=config.model_id,
            messages=msgs,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        key = settings.anthropic_api_key
        self.client = AsyncAnthropic(api_key=key.get_secret_value() if key else None)

    async def complete(
        self, messages: list[Message], config: ModelConfig, *, system: str | None = None
    ) -> CompletionResult:
        response = await self.client.messages.create(
            model=config.model_id,
            max_tokens=config.max_tokens,
            system=system or "",
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        content = response.content[0].text if response.content else ""
        return CompletionResult(
            content=content,
            provider=ModelProvider.ANTHROPIC,
            model_id=config.model_id,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
            },
        )

    async def stream(
        self, messages: list[Message], config: ModelConfig, *, system: str | None = None
    ) -> AsyncIterator[str]:
        async with self.client.messages.stream(
            model=config.model_id,
            max_tokens=config.max_tokens,
            system=system or "",
            messages=[{"role": m.role, "content": m.content} for m in messages],
        ) as stream:
            async for text in stream.text_stream:
                yield text


class GeminiProvider(LLMProvider):
    """Google Gemini — generous free tier (https://aistudio.google.com/apikey)."""

    def __init__(self):
        settings = get_settings()
        self._key = settings.google_ai_api_key

    def _client(self, config: ModelConfig, system: str | None):
        import google.generativeai as genai

        genai.configure(api_key=self._key.get_secret_value() if self._key else None)
        return genai.GenerativeModel(model_name=config.model_id, system_instruction=system or None)

    @staticmethod
    def _to_contents(messages: list[Message]) -> list[dict]:
        return [
            {"role": "model" if m.role == "assistant" else "user", "parts": [m.content]}
            for m in messages
        ]

    async def complete(
        self, messages: list[Message], config: ModelConfig, *, system: str | None = None
    ) -> CompletionResult:
        model = self._client(config, system)
        response = await model.generate_content_async(
            self._to_contents(messages),
            generation_config={
                "max_output_tokens": config.max_tokens,
                "temperature": config.temperature,
            },
        )
        usage = getattr(response, "usage_metadata", None)
        return CompletionResult(
            content=response.text or "",
            provider=ModelProvider.GOOGLE,
            model_id=config.model_id,
            usage={
                "prompt_tokens": getattr(usage, "prompt_token_count", 0) if usage else 0,
                "completion_tokens": getattr(usage, "candidates_token_count", 0) if usage else 0,
            },
        )

    async def stream(
        self, messages: list[Message], config: ModelConfig, *, system: str | None = None
    ) -> AsyncIterator[str]:
        model = self._client(config, system)
        response = await model.generate_content_async(
            self._to_contents(messages),
            generation_config={
                "max_output_tokens": config.max_tokens,
                "temperature": config.temperature,
            },
            stream=True,
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text


class OllamaProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url

    async def complete(
        self, messages: list[Message], config: ModelConfig, *, system: str | None = None
    ) -> CompletionResult:
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        if system:
            msgs.insert(0, {"role": "system", "content": system})

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": config.model_id, "messages": msgs, "stream": False},
            )
            response.raise_for_status()
            data = response.json()

        return CompletionResult(
            content=data.get("message", {}).get("content", ""),
            provider=ModelProvider.OLLAMA,
            model_id=config.model_id,
        )

    async def stream(
        self, messages: list[Message], config: ModelConfig, *, system: str | None = None
    ) -> AsyncIterator[str]:
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        if system:
            msgs.insert(0, {"role": "system", "content": system})

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={"model": config.model_id, "messages": msgs, "stream": True},
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if content := data.get("message", {}).get("content"):
                            yield content


class Brain:
    """Central intelligence orchestrator with multi-model failover."""

    def __init__(self):
        # Providers are constructed lazily so that missing (paid) API keys never
        # break startup in the zero-cost configuration.
        self._provider_cache: dict[ModelProvider, LLMProvider] = {}
        self._provider_factories: dict[ModelProvider, type[LLMProvider]] = {
            ModelProvider.OPENAI: OpenAIProvider,
            ModelProvider.ANTHROPIC: AnthropicProvider,
            ModelProvider.GOOGLE: GeminiProvider,
            ModelProvider.OLLAMA: OllamaProvider,
        }

    def _provider(self, provider: ModelProvider) -> LLMProvider | None:
        if provider not in self._provider_cache:
            factory = self._provider_factories.get(provider)
            if factory is None:
                return None
            try:
                self._provider_cache[provider] = factory()
            except Exception as e:  # noqa: BLE001
                logger.warning("provider_init_failed", provider=provider.value, error=str(e)[:120])
                return None
        return self._provider_cache.get(provider)

    def _get_available_models(self, models: list[ModelConfig]) -> list[ModelConfig]:
        settings = get_settings()
        available = []
        for m in sorted(models, key=lambda x: x.priority):
            if m.provider == ModelProvider.OPENAI and settings.openai_api_key:
                available.append(m)
            elif m.provider == ModelProvider.ANTHROPIC and settings.anthropic_api_key:
                available.append(m)
            elif m.provider == ModelProvider.GOOGLE and settings.google_ai_api_key:
                available.append(m)
            elif m.provider == ModelProvider.OLLAMA:
                # Always a candidate (local, free). Failover handles it being offline.
                # Use the configured local chat model (upgradeable via OLLAMA_CHAT_MODEL).
                available.append(
                    ModelConfig(
                        provider=ModelProvider.OLLAMA,
                        model_id=settings.ollama_chat_model,
                        max_tokens=m.max_tokens,
                        temperature=m.temperature,
                        priority=m.priority,
                    )
                )
        return available

    async def think(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        model_tier: str = "default",
    ) -> CompletionResult:
        from rudra.core.config import get_settings
        from rudra.jarvis.events import EventType, get_event_bus
        from rudra.jarvis.guardrails import scan_and_redact
        from rudra.jarvis.telemetry import log_inference_telemetry

        settings = get_settings()
        bus = get_event_bus()
        bus.publish(EventType.INFERENCE_START, {"tier": model_tier})

        safe_messages = messages
        if settings.enable_guardrails and model_tier in ("reasoning", "default"):
            redacted = []
            for m in messages:
                scan = scan_and_redact(m.content)
                redacted.append(Message(role=m.role, content=scan.redacted_text))
            safe_messages = redacted

        started = time.time()
        model_map = {
            "default": DEFAULT_MODELS,
            "reasoning": REASONING_MODELS,
            "fast": FAST_MODELS,
        }
        models = self._get_available_models(model_map.get(model_tier, DEFAULT_MODELS))

        if not models:
            raise RuntimeError("No AI providers configured. Set API keys in .env")

        last_error = None
        for config in models:
            provider = self._provider(config.provider)
            if not provider:
                continue
            try:
                result = await provider.complete(safe_messages, config, system=system)
                latency = int((time.time() - started) * 1000)
                log_inference_telemetry(
                    model=result.model_id,
                    provider=result.provider.value,
                    latency_ms=latency,
                    prompt_tokens=result.usage.get("prompt_tokens", 0),
                    completion_tokens=result.usage.get("completion_tokens", 0),
                    route="local" if result.provider.value == "ollama" else "cloud",
                )
                bus.publish(
                    EventType.INFERENCE_END,
                    {"provider": result.provider.value, "model": result.model_id},
                )
                logger.info(
                    "brain_completion",
                    provider=config.provider.value,
                    model=config.model_id,
                )
                return result
            except Exception as e:
                last_error = e
                logger.warning("brain_provider_failed", provider=config.provider.value, error=str(e))

        raise RuntimeError(f"All providers failed: {last_error}")

    async def stream_think(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        model_tier: str = "default",
    ) -> AsyncIterator[str]:
        models = self._get_available_models(
            DEFAULT_MODELS if model_tier == "default" else FAST_MODELS
        )
        if not models:
            raise RuntimeError("No AI providers configured")

        for config in models:
            provider = self._provider(config.provider)
            if not provider:
                continue
            async for chunk in provider.stream(messages, config, system=system):
                yield chunk
            return
