"""JWT token creation and validation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException

from app.config import settings


@dataclass
class TokenPayload:
    user_id: str
    jti: str
    exp: datetime
    iat: datetime


def create_access_token(user_id: str) -> tuple[str, TokenPayload]:
    """Create a JWT access token. Returns (token_string, payload)."""
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "jti": jti,
        "iat": now,
        "exp": exp,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token, TokenPayload(user_id=str(user_id), jti=jti, exp=exp, iat=now)


def create_refresh_token(user_id: str) -> tuple[str, TokenPayload]:
    """Create a JWT refresh token with longer TTL."""
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    exp = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "jti": jti,
        "iat": now,
        "exp": exp,
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token, TokenPayload(user_id=str(user_id), jti=jti, exp=exp, iat=now)


def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a JWT access token. Raises 401 on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["sub", "jti", "exp", "iat"]},
        )
        return TokenPayload(
            user_id=payload["sub"],
            jti=payload["jti"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def decode_refresh_token(token: str) -> TokenPayload:
    """Decode and validate a refresh token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["sub", "jti", "exp", "iat", "type"]},
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Not a refresh token")
        return TokenPayload(
            user_id=payload["sub"],
            jti=payload["jti"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")