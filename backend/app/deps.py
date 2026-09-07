"""Dependency injection: get_current_user, require_admin, get_repo.

All user-data queries MUST filter by user_id through these dependencies.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.security.jwt import decode_access_token, TokenPayload


# ── Current user ──────────────────────────────────────────────────────


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Extract and validate JWT from httpOnly cookie or Authorization header.

    Raises 401 if token is missing, expired, revoked, or invalid.
    Returns the user ORM object.
    """
    token: Optional[str] = None

    # 1. Check httpOnly cookie first
    token = request.cookies.get("access_token")

    # 2. Fall back to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    payload: TokenPayload = decode_access_token(token)

    # Check if token is revoked (blacklist)
    from app.models.auth import RevokedToken

    result = await db.execute(
        select(RevokedToken).where(RevokedToken.jti == payload.jti)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=401, detail="Token has been revoked")

    # Load user
    from app.models.auth import User

    result = await db.execute(select(User).where(User.id == payload.user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


# ── Optional user (for public + authenticated hybrid endpoints) ────────


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Like get_current_user but returns None instead of raising 401."""
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None


# ── Admin guard ────────────────────────────────────────────────────────


async def require_admin(
    current_user=Depends(get_current_user),
):
    """Ensure the current user has admin role."""
    if not getattr(current_user, "is_admin", False) and getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ── User ID shortcut ───────────────────────────────────────────────────


async def get_current_user_id(
    current_user=Depends(get_current_user),
) -> UUID:
    """Convenience: just return the user_id (for filtering queries)."""
    return current_user.id