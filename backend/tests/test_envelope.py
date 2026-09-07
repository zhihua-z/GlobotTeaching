"""Unit tests for the response envelope and error handling."""

from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.envelope import (
    ErrorDetail,
    Envelope,
    error_response,
    register_exception_handlers,
    success_response,
)
from app.routers.health import router as health_router


class TestSuccessResponse:
    """Tests for success_response()."""

    def test_wraps_dict_in_data(self) -> None:
        result = success_response({"key": "value"})
        assert result == {"data": {"key": "value"}}

    def test_wraps_list_in_data(self) -> None:
        result = success_response([1, 2, 3])
        assert result == {"data": [1, 2, 3]}

    def test_wraps_none_in_data(self) -> None:
        result = success_response(None)
        assert result == {"data": None}

    def test_wraps_string_in_data(self) -> None:
        result = success_response("message")
        assert result == {"data": "message"}

    def test_wraps_empty_dict(self) -> None:
        result = success_response({})
        assert result == {"data": {}}


class TestErrorResponse:
    """Tests for error_response()."""

    def test_basic_error(self) -> None:
        result = error_response("NOT_FOUND", "Resource not found")
        assert result == {
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found",
                "field": None,
            }
        }

    def test_error_with_field(self) -> None:
        result = error_response("VALIDATION_FAILED", "Invalid email", field="email")
        assert result["error"]["code"] == "VALIDATION_FAILED"
        assert result["error"]["message"] == "Invalid email"
        assert result["error"]["field"] == "email"

    def test_error_codes_are_present(self) -> None:
        expected_codes = [
            "AUTH_REQUIRED",
            "FORBIDDEN",
            "NOT_FOUND",
            "CONFLICT",
            "VALIDATION_FAILED",
            "RATE_LIMITED",
        ]
        for code in expected_codes:
            result = error_response(code, "test")
            assert result["error"]["code"] == code

    def test_no_data_field_in_error(self) -> None:
        result = error_response("INTERNAL", "Server error")
        assert "data" not in result


class TestErrorDetailModel:
    """Tests for the ErrorDetail Pydantic model."""

    def test_construct_with_all_fields(self) -> None:
        detail = ErrorDetail(code="AUTH_REQUIRED", message="Please login", field="token")
        assert detail.code == "AUTH_REQUIRED"
        assert detail.message == "Please login"
        assert detail.field == "token"

    def test_construct_without_optional_field(self) -> None:
        detail = ErrorDetail(code="NOT_FOUND", message="Not found")
        assert detail.field is None

    def test_serialize_to_dict(self) -> None:
        detail = ErrorDetail(code="FORBIDDEN", message="Access denied", field="role")
        d = detail.model_dump()
        assert d == {"code": "FORBIDDEN", "message": "Access denied", "field": "role"}


class TestEnvelopeModel:
    """Tests for the Envelope Pydantic model."""

    def test_success_envelope(self) -> None:
        env = Envelope(data={"result": 42})
        assert env.data == {"result": 42}
        assert env.error is None

    def test_error_envelope(self) -> None:
        env = Envelope(
            error=ErrorDetail(code="INTERNAL", message="Boom")
        )
        assert env.data is None
        assert env.error is not None
        assert env.error.code == "INTERNAL"

    def test_envelope_serialization(self) -> None:
        env = Envelope(data="hello")
        d = env.model_dump()
        assert d == {"data": "hello", "error": None}


class TestExceptionHandlers:
    """Integration tests for global exception handlers via a test app."""

    @pytest.fixture
    def test_app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(health_router)

        @app.get("/test-http-error")
        async def raise_http_error():
            raise HTTPException(status_code=404, detail="Custom not found")

        @app.get("/test-server-error")
        async def raise_server_error():
            raise RuntimeError("Unexpected failure")

        register_exception_handlers(app)
        return app

    @pytest.fixture
    def client(self, test_app: FastAPI) -> TestClient:
        return TestClient(test_app, raise_server_exceptions=False)

    def test_health_endpoint_works(self, client: TestClient) -> None:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data

    def test_http_404_uses_envelope(self, client: TestClient) -> None:
        resp = client.get("/test-http-error")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
        assert "Custom not found" in data["error"]["message"]

    def test_http_401_uses_auth_required_code(self, client: TestClient) -> None:
        @client.app.get("/test-401")  # type: ignore
        async def raise_401():
            raise HTTPException(status_code=401, detail="Token expired")

        resp = client.get("/test-401")
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "AUTH_REQUIRED"

    def test_http_403_uses_forbidden_code(self, client: TestClient) -> None:
        @client.app.get("/test-403")  # type: ignore
        async def raise_403():
            raise HTTPException(status_code=403, detail="Admin only")

        resp = client.get("/test-403")
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN"

    def test_http_409_uses_conflict_code(self, client: TestClient) -> None:
        @client.app.get("/test-409")  # type: ignore
        async def raise_409():
            raise HTTPException(status_code=409, detail="Duplicate entry")

        resp = client.get("/test-409")
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "CONFLICT"

    def test_http_422_uses_validation_code(self, client: TestClient) -> None:
        @client.app.get("/test-422")  # type: ignore
        async def raise_422():
            raise HTTPException(
                status_code=422, detail="Validation error"
            )

        resp = client.get("/test-422")
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_FAILED"

    def test_server_error_returns_500_envelope(self, client: TestClient) -> None:
        resp = client.get("/test-server-error")
        assert resp.status_code == 500
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "INTERNAL"

    def test_unhandled_route_returns_envelope(self, client: TestClient) -> None:
        resp = client.get("/api/v1/nonexistent")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"