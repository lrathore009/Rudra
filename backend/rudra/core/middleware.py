"""Security middleware — rate limiting and response headers."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from rudra.core.config import get_settings

# Paths exempt from rate limiting (health probes).
_RATE_LIMIT_EXEMPT = {"/api/v1/health", "/api/v1/health/services", "/docs", "/openapi.json", "/redoc"}

# Sensitive endpoints with stricter limits (requests per minute).
_RATE_LIMIT_STRICT_PREFIXES = (
    "/api/v1/command",
    "/api/v1/agent",
    "/api/v1/memories",
    "/api/v1/research",
    "/api/v1/documents",
    "/api/v1/auth/login",
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-process sliding-window rate limiter (local-first; optional Redis later)."""

    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.limit = requests_per_minute
        self.strict_limit = max(20, requests_per_minute // 3)
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _allow(self, key: str, limit: int) -> bool:
        now = time.time()
        window_start = now - 60.0
        bucket = self._hits[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        limit = settings.rate_limit_per_minute
        strict_limit = max(20, limit // 3)

        path = request.url.path
        if path in _RATE_LIMIT_EXEMPT or request.method == "OPTIONS":
            return await call_next(request)

        effective_limit = strict_limit if path.startswith(_RATE_LIMIT_STRICT_PREFIXES) else limit
        key = f"{self._client_key(request)}:{path.split('/')[1:3]}"
        if not self._allow(key, effective_limit):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again in a minute."},
            )
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "microphone=(self), camera=()")
        response.headers.setdefault("X-Rudra-Security", "enabled")
        if get_settings().is_production:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains",
            )
        return response
