"""Auth router: login, logout, refresh, me."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user, get_optional_user
from app.envelope import success_response
from app.models.auth import User, RevokedToken
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.security.passwords import verify_password, hash_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# ── Helper: set auth cookies ──────────────────────────────────────────


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set httpOnly cookies for access and refresh tokens."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production (HTTPS)
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    """Clear auth cookies."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")


# ── POST /auth/login ──────────────────────────────────────────────────


@router.post("/login", response_model=dict)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and set httpOnly cookies.

    Frontend: /login page
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    # Constant-time-ish: always verify hash even if user doesn't exist
    if user is None:
        # Verify against a dummy hash to prevent timing attacks
        verify_password(body.password, "$2b$12$dummyhashfordummyuser12345678901234567890")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    # Update last_login_at
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    # Create tokens
    access_token, _ = create_access_token(str(user.id))
    refresh_token, refresh_payload = create_refresh_token(str(user.id))

    # Set cookies
    _set_auth_cookies(response, access_token, refresh_token)

    return success_response({
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "is_admin": user.is_admin,
            "display_name": user.display_name,
            "is_active": user.is_active,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
    })


# ── POST /auth/logout ─────────────────────────────────────────────────


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Logout: revoke access token and clear cookies.

    Requires valid access token (cookie or header).
    """
    # Try to get and revoke the token
    token: str | None = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if token:
        try:
            from app.security.jwt import decode_access_token
            payload = decode_access_token(token)
            # Revoke the token
            revoked = RevokedToken(
                jti=payload.jti,
                user_id=payload.user_id,
                expires_at=payload.exp,
            )
            db.add(revoked)
            await db.commit()
        except Exception:
            # Token might be invalid/expired — still clear cookies
            pass

    _clear_auth_cookies(response)
    return success_response({"message": "Logged out"})


# ── POST /auth/refresh ────────────────────────────────────────────────


@router.post("/refresh", response_model=dict)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Exchange refresh token for new access + refresh token pair."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token required")

    payload = decode_refresh_token(refresh_token)

    # Check if refresh token is revoked
    result = await db.execute(
        select(RevokedToken).where(RevokedToken.jti == payload.jti)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    # Verify user exists and is active
    result = await db.execute(select(User).where(User.id == payload.user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Revoke old refresh token
    revoked = RevokedToken(
        jti=payload.jti,
        user_id=payload.user_id,
        expires_at=payload.exp,
    )
    db.add(revoked)

    # Issue new tokens
    new_access, _ = create_access_token(str(user.id))
    new_refresh, _ = create_refresh_token(str(user.id))
    await db.commit()

    _set_auth_cookies(response, new_access, new_refresh)

    return success_response({"message": "Token refreshed"})


# ── GET /auth/me ──────────────────────────────────────────────────────


@router.get("/me", response_model=dict)
async def me(
    current_user: User = Depends(get_current_user),
):
    """Get current user info. Used by middleware guard on all protected pages.

    All protected pages on frontend call this to verify auth.
    """
    return success_response({
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role,
            "is_admin": current_user.is_admin,
            "display_name": current_user.display_name,
            "is_active": current_user.is_active,
            "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        }
    })