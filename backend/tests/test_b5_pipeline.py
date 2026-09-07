"""Tests for B5 Pipeline + Review + Evals routers."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _get_admin_headers(db_session) -> dict:
    """Create a test admin user and return auth headers."""
    from app.models.auth import User
    from app.security.passwords import hash_password
    from app.security.jwt import create_access_token

    user = User(
        email="b5admin@test.com",
        password_hash=hash_password("testpass"),
        role="admin",
        is_admin=True,
        display_name="B5 Admin",
    )
    db_session.add(user)
    await db_session.flush()

    token, _ = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


# ─── Pipeline ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_pipeline_runs_empty(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.get("/api/v1/admin/pipeline/runs", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_pipeline_upload(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.post(
        "/api/v1/admin/pipeline/upload",
        headers=headers,
        files={"file": ("test.md", b"# Test question", "text/markdown")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["input_file"] == "test.md"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_pipeline_get_not_found(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.get(
        "/api/v1/admin/pipeline/runs/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_pipeline_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/admin/pipeline/runs")
    assert resp.status_code == 401


# ─── Review ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_review_queue_empty(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.get("/api/v1/admin/review/queue", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_review_get_draft_not_found(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.get(
        "/api/v1/admin/review/queue/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_review_approve_draft_not_found(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.post(
        "/api/v1/admin/review/queue/00000000-0000-0000-0000-000000000000/approve",
        json={"reviewer": "admin"},
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_review_reject_draft_not_found(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.post(
        "/api/v1/admin/review/queue/00000000-0000-0000-0000-000000000000/reject",
        json={"reason": "Invalid", "reviewer": "admin"},
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_review_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/admin/review/queue")
    assert resp.status_code == 401


# ─── Evals ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_eval_sets_empty(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.get("/api/v1/admin/evals/sets", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_create_eval_set_lifecycle(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)

    # Create
    resp = await client.post(
        "/api/v1/admin/evals/sets",
        json={"name": "test-eval-set", "description": "A test eval set"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test-eval-set"
    assert data["case_count"] == 0
    set_id = data["id"]

    # Duplicate
    resp = await client.post(
        "/api/v1/admin/evals/sets",
        json={"name": "test-eval-set"},
        headers=headers,
    )
    assert resp.status_code == 409

    # Get
    resp = await client.get(f"/api/v1/admin/evals/sets/{set_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "test-eval-set"

    # List
    resp = await client.get("/api/v1/admin/evals/sets", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # Add case
    resp = await client.post(
        "/api/v1/admin/evals/cases",
        json={
            "eval_set_id": set_id,
            "input": {"q": "test"},
            "expected_output": {"a": "answer"},
        },
        headers=headers,
    )
    assert resp.status_code == 201

    # Create run
    resp = await client.post(
        "/api/v1/admin/evals/runs",
        json={"eval_set_id": set_id},
        headers=headers,
    )
    assert resp.status_code == 201
    run_id = resp.json()["id"]

    # List runs
    resp = await client.get("/api/v1/admin/evals/runs", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # Get run
    resp = await client.get(f"/api/v1/admin/evals/runs/{run_id}", headers=headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_eval_set_not_found(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.get(
        "/api/v1/admin/evals/sets/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_eval_case_invalid_set(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.post(
        "/api/v1/admin/evals/cases",
        json={
            "eval_set_id": "00000000-0000-0000-0000-000000000000",
            "input": {"q": "test"},
            "expected_output": {"a": "answer"},
        },
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_eval_run_not_found(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.get(
        "/api/v1/admin/evals/runs/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_eval_run_invalid_set(client: AsyncClient, db_session):
    headers = await _get_admin_headers(db_session)
    resp = await client.post(
        "/api/v1/admin/evals/runs",
        json={"eval_set_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_evals_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/admin/evals/sets")
    assert resp.status_code == 401