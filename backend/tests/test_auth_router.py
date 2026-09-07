"""Tests for the auth router: login, logout, me, refresh.

Uses the existing conftest.py fixtures (db_session, client) which create
a fresh SQLite database per test function.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.security.passwords import hash_password


async def _create_user(
    db: AsyncSession,
    *,
    email: str = "test@example.com",
    password: str = "securepassword",
    is_admin: bool = False,
    is_active: bool = True,
    display_name: str | None = None,
) -> str:
    """Helper: create a user directly in the DB. Returns user_id string."""
    from app.models.auth import User

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email=email,
        password_hash=hash_password(password),
        role="admin" if is_admin else "student",
        is_admin=is_admin,
        is_active=is_active,
        display_name=display_name,
    )
    db.add(user)
    await db.commit()
    return str(user_id)


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient, db_session: AsyncSession) -> None:
        await _create_user(db_session, email="user@test.com", password="pass123")

        resp = await client.post("/api/v1/auth/login", json={
            "email": "user@test.com",
            "password": "pass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert data["data"]["user"]["email"] == "user@test.com"
        assert data["data"]["user"]["role"] == "student"
        assert data["data"]["user"]["is_active"] is True

    async def test_login_sets_cookies(self, client: AsyncClient, db_session: AsyncSession) -> None:
        await _create_user(db_session, email="cookie@test.com", password="pass")

        resp = await client.post("/api/v1/auth/login", json={
            "email": "cookie@test.com",
            "password": "pass",
        })
        assert resp.status_code == 200
        # Check cookies are set in response
        cookies = resp.cookies
        assert "access_token" in cookies
        assert "refresh_token" in cookies
        # httpOnly is sent in Set-Cookie but httpx doesn't parse that easily;
        # just verify the cookies exist

    async def test_login_wrong_password(self, client: AsyncClient, db_session: AsyncSession) -> None:
        await _create_user(db_session, email="user@test.com", password="correct")

        resp = await client.post("/api/v1/auth/login", json={
            "email": "user@test.com",
            "password": "wrong-password",
        })
        assert resp.status_code == 401
        data = resp.json()
        assert data["error"]["code"] == "AUTH_REQUIRED"

    async def test_login_nonexistent_user(self, client: AsyncClient, db_session: AsyncSession) -> None:
        resp = await client.post("/api/v1/auth/login", json={
            "email": "noone@test.com",
            "password": "any",
        })
        assert resp.status_code == 401
        data = resp.json()
        assert data["error"]["code"] == "AUTH_REQUIRED"
        # Message should NOT reveal if user exists
        assert "Invalid email or password" in data["error"]["message"]

    async def test_login_disabled_user(self, client: AsyncClient, db_session: AsyncSession) -> None:
        await _create_user(db_session, email="disabled@test.com", password="pass", is_active=False)

        resp = await client.post("/api/v1/auth/login", json={
            "email": "disabled@test.com",
            "password": "pass",
        })
        assert resp.status_code == 403
        data = resp.json()
        assert data["error"]["code"] == "FORBIDDEN"
        assert "disabled" in data["error"]["message"].lower()

    async def test_login_updates_last_login(self, client: AsyncClient, db_session: AsyncSession) -> None:
        await _create_user(db_session, email="login@test.com", password="pass")

        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@test.com",
            "password": "pass",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["user"]["last_login_at"] is not None

    async def test_login_missing_fields(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/login", json={})
        assert resp.status_code == 422

    async def test_login_empty_email(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/login", json={
            "email": "",
            "password": "something",
        })
        assert resp.status_code == 422

    async def test_login_empty_password(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/login", json={
            "email": "user@test.com",
            "password": "",
        })
        assert resp.status_code == 422

    async def test_login_admin_user(self, client: AsyncClient, db_session: AsyncSession) -> None:
        await _create_user(db_session, email="admin@test.com", password="admin", is_admin=True)

        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "admin",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["user"]["is_admin"] is True
        assert data["data"]["user"]["role"] == "admin"


class TestLogout:
    """Tests for POST /api/v1/auth/logout."""

    async def _login_and_get_cookies(self, client: AsyncClient, db_session: AsyncSession) -> dict:
        """Helper: login and return the cookies dict."""
        await _create_user(db_session, email="logout@test.com", password="test")
        resp = await client.post("/api/v1/auth/login", json={
            "email": "logout@test.com",
            "password": "test",
        })
        return dict(resp.cookies)

    async def test_logout_with_valid_token(self, client: AsyncClient, db_session: AsyncSession) -> None:
        cookies = await self._login_and_get_cookies(client, db_session)

        resp = await client.post("/api/v1/auth/logout", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["message"] == "Logged out"

    async def test_logout_clears_cookies(self, client: AsyncClient, db_session: AsyncSession) -> None:
        cookies = await self._login_and_get_cookies(client, db_session)

        resp = await client.post("/api/v1/auth/logout", cookies=cookies)
        assert resp.status_code == 200
        # After logout, cookies should be cleared
        # httpx stores cleared cookies; we check Set-Cookie headers
        set_cookie_headers = resp.headers.get_list("set-cookie")
        assert any("access_token=;" in h or 'access_token="";' in h for h in set_cookie_headers)

    async def test_logout_without_token(self, client: AsyncClient) -> None:
        """Logout without any auth should still succeed (already logged out)."""
        resp = await client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["message"] == "Logged out"

    async def test_logout_revokes_token(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """After logout, the access token should no longer work."""
        cookies = await self._login_and_get_cookies(client, db_session)

        # Logout
        await client.post("/api/v1/auth/logout", cookies=cookies)

        # Try to use the revoked token
        resp = await client.get("/api/v1/auth/me", cookies=cookies)
        assert resp.status_code == 401

    async def test_logout_with_header_token(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """Logout with token in Authorization header instead of cookie."""
        await _create_user(db_session, email="header@test.com", password="test")
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "header@test.com",
            "password": "test",
        })
        # Extract access token from cookie
        access_token = login_resp.cookies.get("access_token")

        # Logout using Authorization header
        resp = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200


class TestMe:
    """Tests for GET /api/v1/auth/me."""

    async def _login(self, client: AsyncClient, db_session: AsyncSession) -> dict:
        """Login and return cookies."""
        await _create_user(db_session, email="me@test.com", password="test", display_name="Test User")
        resp = await client.post("/api/v1/auth/login", json={
            "email": "me@test.com",
            "password": "test",
        })
        return dict(resp.cookies)

    async def test_me_authenticated(self, client: AsyncClient, db_session: AsyncSession) -> None:
        cookies = await self._login(client, db_session)

        resp = await client.get("/api/v1/auth/me", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["user"]["email"] == "me@test.com"
        assert data["data"]["user"]["display_name"] == "Test User"
        assert data["data"]["user"]["is_active"] is True

    async def test_me_unauthenticated(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401
        data = resp.json()
        assert data["error"]["code"] == "AUTH_REQUIRED"

    async def test_me_with_invalid_token(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/v1/auth/me",
            cookies={"access_token": "invalid-token-value"},
        )
        assert resp.status_code == 401

    async def test_me_with_bearer_header(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """Auth should work with Bearer token in Authorization header."""
        await _create_user(db_session, email="bearer@test.com", password="test")
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "bearer@test.com",
            "password": "test",
        })
        access_token = login_resp.cookies.get("access_token")

        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["user"]["email"] == "bearer@test.com"

    async def test_me_returns_user_id(self, client: AsyncClient, db_session: AsyncSession) -> None:
        cookies = await self._login(client, db_session)

        resp = await client.get("/api/v1/auth/me", cookies=cookies)
        assert resp.status_code == 200
        user_data = resp.json()["data"]["user"]
        assert "id" in user_data
        # Should be a valid UUID string
        uuid.UUID(user_data["id"])


class TestRefresh:
    """Tests for POST /api/v1/auth/refresh."""

    async def _get_refresh_cookies(self, client: AsyncClient, db_session: AsyncSession) -> dict:
        """Login and return cookies including refresh_token."""
        await _create_user(db_session, email="refresh@test.com", password="test")
        resp = await client.post("/api/v1/auth/login", json={
            "email": "refresh@test.com",
            "password": "test",
        })
        return dict(resp.cookies)

    async def test_refresh_success(self, client: AsyncClient, db_session: AsyncSession) -> None:
        cookies = await self._get_refresh_cookies(client, db_session)

        resp = await client.post("/api/v1/auth/refresh", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert "Token refreshed" in data["data"]["message"]

    async def test_refresh_sets_new_cookies(self, client: AsyncClient, db_session: AsyncSession) -> None:
        cookies = await self._get_refresh_cookies(client, db_session)

        resp = await client.post("/api/v1/auth/refresh", cookies=cookies)
        assert resp.status_code == 200
        # New access_token should be set
        new_cookies = dict(resp.cookies)
        assert "access_token" in new_cookies or any(
            "access_token=" in h for h in resp.headers.get_list("set-cookie")
        )

    async def test_refresh_without_token(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/refresh")
        assert resp.status_code == 401

    async def test_refresh_with_invalid_token(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/refresh",
            cookies={"refresh_token": "invalid"},
        )
        assert resp.status_code == 401

    async def test_refresh_user_deactivated(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """If user is deactivated after login, refresh should fail."""
        cookies = await self._get_refresh_cookies(client, db_session)

        # Deactivate the user
        from app.models.auth import User
        from sqlalchemy import select, update
        await db_session.execute(
            update(User).where(User.email == "refresh@test.com").values(is_active=False)
        )
        await db_session.commit()

        resp = await client.post("/api/v1/auth/refresh", cookies=cookies)
        assert resp.status_code == 401


class TestAuthEnvelopeConsistency:
    """Verify all auth responses use the {data, error} envelope."""

    async def test_success_responses_have_data_key(self, client: AsyncClient, db_session: AsyncSession) -> None:
        await _create_user(db_session, email="env@test.com", password="test")
        resp = await client.post("/api/v1/auth/login", json={
            "email": "env@test.com",
            "password": "test",
        })
        assert "data" in resp.json()
        assert "error" not in resp.json()

    async def test_error_responses_have_error_key(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/auth/me")
        assert "error" in resp.json()
        assert "code" in resp.json()["error"]
        assert "message" in resp.json()["error"]


class TestAuthSecurity:
    """Security-related test cases."""

    async def test_no_user_enumeration_on_login(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """Login should return identical error for wrong email vs wrong password."""
        await _create_user(db_session, email="real@test.com", password="correct")

        # Wrong password for existing user
        resp1 = await client.post("/api/v1/auth/login", json={
            "email": "real@test.com",
            "password": "wrong",
        })
        assert resp1.status_code == 401

        # Non-existent user
        resp2 = await client.post("/api/v1/auth/login", json={
            "email": "fake@test.com",
            "password": "anything",
        })
        assert resp2.status_code == 401

        # Both should have identical error messages (preventing user enumeration)
        assert resp1.json()["error"]["message"] == resp2.json()["error"]["message"]