"""Auth schemas: request/response for login, logout, user info."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Request schemas ──────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    pass  # refresh token comes from cookie


# ── Response schemas ─────────────────────────────────────────────────


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    is_admin: bool
    display_name: Optional[str] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    user: UserResponse


class MeResponse(BaseModel):
    user: UserResponse