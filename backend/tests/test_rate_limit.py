"""Unit tests for the rate limiting middleware."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.security.rate_limit import RateLimitMiddleware


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=5,
        window_seconds=1,
    )

    @app.get("/api/v1/test")
    async def test_endpoint():
        return {"data": "ok"}

    @app.get("/api/v1/auth/login")
    async def login_endpoint():
        return {"data": "login"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


class TestRateLimitBasic:
    """Basic rate limiting behavior."""

    def test_allows_requests_within_limit(self, client: TestClient) -> None:
        for _ in range(5):
            resp = client.get("/api/v1/test")
            assert resp.status_code == 200

    def test_blocks_requests_over_limit(self, client: TestClient) -> None:
        # Send 5 requests (the limit)
        for _ in range(5):
            resp = client.get("/api/v1/test")
            assert resp.status_code == 200

        # 6th request should be rate limited
        resp = client.get("/api/v1/test")
        assert resp.status_code == 429
        data = resp.json()
        assert data["error"]["code"] == "RATE_LIMITED"

    def test_rate_limited_response_structure(self, client: TestClient) -> None:
        # Exhaust requests
        for _ in range(5):
            client.get("/api/v1/test")

        resp = client.get("/api/v1/test")
        assert resp.status_code == 429
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "RATE_LIMITED"
        assert "Too many requests" in data["error"]["message"]


class TestRateLimitNonApiRoutes:
    """Rate limiter should skip non-API routes."""

    def test_health_check_not_rate_limited(self, client: TestClient) -> None:
        """Health endpoint should not be affected by rate limiting."""
        for _ in range(20):
            resp = client.get("/health")
            assert resp.status_code == 200


class TestRateLimitScopedLimits:
    """Different endpoints should have different rate limits."""

    def test_login_has_stricter_limit(self, client: TestClient) -> None:
        """Login should be limited to 10 requests (config default)."""
        # Default limit is 5, but login endpoint has 10
        # So we should be able to make more than 5 login requests
        for i in range(6):
            resp = client.get("/api/v1/auth/login")
            # Should still be allowed after 5 requests (login has limit 10)
            assert resp.status_code == 200, f"Request {i + 1} was blocked"

    def test_different_paths_have_separate_buckets(self, client: TestClient) -> None:
        """Different API path prefixes should have independent rate limit counters."""
        # Exhaust /api/v1/test (bucket: /api/v1)
        for _ in range(5):
            client.get("/api/v1/test")

        # /api/v2/other should still work (bucket: /api/v2)
        @client.app.get("/api/v2/other")  # type: ignore
        async def other():
            return {"data": "other"}

        resp = client.get("/api/v2/other")
        assert resp.status_code == 200


class TestRateLimitWindowReset:
    """Rate limit window should reset after the window expires."""

    @patch("time.time")
    def test_window_reset_after_expiry(self, mock_time: patch, client: TestClient) -> None:
        # Set initial time
        mock_time.return_value = 1000.0

        # Exhaust requests
        for _ in range(5):
            resp = client.get("/api/v1/test")
            assert resp.status_code == 200

        # 6th should be blocked
        resp = client.get("/api/v1/test")
        assert resp.status_code == 429

        # Advance time past the window (1 second)
        mock_time.return_value = 1000.0 + 1.5

        # Now we should be able to make requests again
        resp = client.get("/api/v1/test")
        assert resp.status_code == 200