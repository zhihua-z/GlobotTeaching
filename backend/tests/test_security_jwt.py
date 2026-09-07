"""Unit tests for JWT token creation and validation."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from fastapi import HTTPException

from app.security.jwt import (
    TokenPayload,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


class TestCreateAccessToken:
    """Tests for create_access_token()."""

    def test_returns_token_and_payload(self) -> None:
        token, payload = create_access_token("test-user-id")
        assert isinstance(token, str)
        assert isinstance(payload, TokenPayload)
        assert payload.user_id == "test-user-id"

    def test_token_is_valid_jwt(self) -> None:
        token, _ = create_access_token("user-123")
        # Should be 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3

    def test_payload_contains_required_fields(self) -> None:
        _, payload = create_access_token("user-456")
        assert payload.user_id == "user-456"
        assert payload.jti is not None
        assert len(payload.jti) > 0
        assert payload.exp > payload.iat

    def test_token_expiry_is_in_future(self) -> None:
        _, payload = create_access_token("user")
        now = datetime.now(timezone.utc)
        assert payload.exp > now

    def test_unique_jti_per_token(self) -> None:
        _, p1 = create_access_token("user")
        _, p2 = create_access_token("user")
        assert p1.jti != p2.jti

    def test_token_expiry_within_expected_window(self) -> None:
        _, payload = create_access_token("user")
        now = datetime.now(timezone.utc)
        # Should expire within ~25 hours (config default is 24h)
        max_expiry = now + timedelta(hours=25)
        assert payload.exp <= max_expiry


class TestCreateRefreshToken:
    """Tests for create_refresh_token()."""

    def test_returns_token_and_payload(self) -> None:
        token, payload = create_refresh_token("user-1")
        assert isinstance(token, str)
        assert isinstance(payload, TokenPayload)
        assert payload.user_id == "user-1"

    def test_refresh_token_lives_longer_than_access(self) -> None:
        _, access = create_access_token("user")
        _, refresh = create_refresh_token("user")
        # Refresh should expire after access
        assert refresh.exp > access.exp

    def test_refresh_token_has_type_claim(self) -> None:
        token, _ = create_refresh_token("user")
        decoded = jwt.decode(
            token,
            options={"verify_signature": False},
        )
        assert decoded.get("type") == "refresh"

    def test_unique_jti(self) -> None:
        _, p1 = create_refresh_token("user")
        _, p2 = create_refresh_token("user")
        assert p1.jti != p2.jti


class TestDecodeAccessToken:
    """Tests for decode_access_token()."""

    def test_decode_valid_token(self) -> None:
        token, original = create_access_token("user-id")
        decoded = decode_access_token(token)
        assert decoded.user_id == original.user_id
        assert decoded.jti == original.jti

    def test_decode_expired_token(self) -> None:
        # Create a token that expired 1 hour ago using a patched expiry
        with patch("app.security.jwt.datetime") as mock_dt:
            fixed_now = datetime(2020, 1, 1, tzinfo=timezone.utc)
            mock_dt.now.return_value = fixed_now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            # Create token with past expiry
            token, _ = create_access_token("user")

        # Now decode should raise 401
        with pytest.raises(HTTPException) as exc:
            decode_access_token(token)
        assert exc.value.status_code == 401

    def test_decode_tampered_token(self) -> None:
        token, _ = create_access_token("user")
        # Tamper with the payload (change last char)
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(HTTPException) as exc:
            decode_access_token(tampered)
        assert exc.value.status_code == 401

    def test_decode_garbage_string(self) -> None:
        with pytest.raises(HTTPException) as exc:
            decode_access_token("not-a-jwt-token")
        assert exc.value.status_code == 401

    def test_decode_empty_string(self) -> None:
        with pytest.raises(HTTPException) as exc:
            decode_access_token("")
        assert exc.value.status_code == 401

    def test_decode_none_raises(self) -> None:
        with pytest.raises(HTTPException):
            decode_access_token(None)  # type: ignore

    def test_decode_wrong_signing_key(self) -> None:
        # Create token with original key
        token, _ = create_access_token("user")
        # Patch the secret key to a different value, so decode fails
        with patch("app.security.jwt.settings.SECRET_KEY", "wrong-key"):
            with pytest.raises(HTTPException) as exc:
                decode_access_token(token)
            assert exc.value.status_code == 401


class TestDecodeRefreshToken:
    """Tests for decode_refresh_token()."""

    def test_decode_valid_refresh_token(self) -> None:
        token, original = create_refresh_token("user")
        decoded = decode_refresh_token(token)
        assert decoded.user_id == original.user_id
        assert decoded.jti == original.jti

    def test_rejects_access_token_as_refresh(self) -> None:
        token, _ = create_access_token("user")
        with pytest.raises(HTTPException) as exc:
            decode_refresh_token(token)
        assert exc.value.status_code == 401

    def test_decode_invalid_refresh_token(self) -> None:
        with pytest.raises(HTTPException) as exc:
            decode_refresh_token("bad-refresh-token")
        assert exc.value.status_code == 401

    def test_decode_empty_refresh_token(self) -> None:
        with pytest.raises(HTTPException) as exc:
            decode_refresh_token("")
        assert exc.value.status_code == 401


class TestTokenPayload:
    """Tests for the TokenPayload dataclass."""

    def test_create_payload(self) -> None:
        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=1)
        payload = TokenPayload(
            user_id="user-1",
            jti="jti-1",
            exp=exp,
            iat=now,
        )
        assert payload.user_id == "user-1"
        assert payload.jti == "jti-1"
        assert payload.exp == exp
        assert payload.iat == now

    def test_payload_equality(self) -> None:
        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=1)
        p1 = TokenPayload("u1", "j1", exp, now)
        p2 = TokenPayload("u1", "j1", exp, now)
        assert p1 == p2

    def test_payload_inequality(self) -> None:
        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=1)
        p1 = TokenPayload("u1", "j1", exp, now)
        p2 = TokenPayload("u2", "j1", exp, now)
        assert p1 != p2