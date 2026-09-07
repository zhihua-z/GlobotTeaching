"""Simple in-memory rate limiting middleware.

For production, replace with Redis-backed limiter (e.g., slowapi).
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token-bucket inspired rate limiter.

    Limits requests per (ip, path_prefix) pair.
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip health check and non-API routes
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # Use a tighter limit for login endpoint
        if request.url.path == "/api/v1/auth/login":
            max_req = 10
            window = self.window_seconds
        elif request.url.path.startswith("/api/v1/chat"):
            max_req = 30
            window = self.window_seconds
        else:
            max_req = self.max_requests
            window = self.window_seconds

        key = f"{client_ip}:{request.url.path.rsplit('/', 1)[0]}"
        now = time.time()

        # Clean expired entries
        self._buckets[key] = [t for t in self._buckets[key] if now - t < window]

        if len(self._buckets[key]) >= max_req:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Too many requests. Please try again later.",
                    }
                },
            )

        self._buckets[key].append(now)
        return await call_next(request)