"""Unified response envelope and global exception handler.

All API responses use this format:
  Success: { "data": ... }
  Error:   { "error": { "code", "message", "field?" } }
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: Optional[str] = None


class Envelope(BaseModel):
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None


# ── Error codes (aligned with frontend §5.2) ──────────────────────────

ERROR_CODES = {
    401: "AUTH_REQUIRED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_FAILED",
    429: "RATE_LIMITED",
    500: "INTERNAL",
}


def success_response(data: Any) -> dict:
    """Wrap data in the standard envelope."""
    return {"data": data}


def error_response(code: str, message: str, field: Optional[str] = None) -> dict:
    """Wrap error in the standard envelope."""
    return {"error": {"code": code, "message": message, "field": field}}


# ── Global Exception Handlers ─────────────────────────────────────────


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = ERROR_CODES.get(exc.status_code, "INTERNAL")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code, exc.detail),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract the first error detail
    field = None
    message = "Validation failed"
    if exc.errors():
        first = exc.errors()[0]
        field = " → ".join(str(loc) for loc in first.get("loc", []))
        message = first.get("msg", message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response("VALIDATION_FAILED", message, field=field),
    )


async def general_exception_handler(request: Request, exc: Exception):
    import logging

    logger = logging.getLogger("globot")
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response("INTERNAL", "An unexpected error occurred"),
    )


def register_exception_handlers(app):
    """Register all exception handlers on the FastAPI app."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)