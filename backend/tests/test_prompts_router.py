"""Tests for /api/v1/admin/prompts endpoints (B4)."""

import pytest
from httpx import AsyncClient

from app.security.jwt import create_access_token
from app.models.auth import User


async def _get_admin_headers(db_session) -> dict:
    """Create a test admin user and return auth headers."""
    from app.models.auth import User
    from app.security.passwords import hash_password

    user = User(
        email="admin@test.com",
        password_hash=hash_password("testpass"),
        role="admin",
        is_admin=True,
        display_name="Test Admin",
    )
    db_session.add(user)
    await db_session.flush()

    token, _ = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_prompts_empty(client: AsyncClient, db_session):
    """GET /admin/prompts when no templates exist."""
    headers = await _get_admin_headers(db_session)
    resp = await client.get("/api/v1/admin/prompts", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_prompts_requires_admin(client: AsyncClient, db_session):
    """GET /admin/prompts without auth returns 401."""
    resp = await client.get("/api/v1/admin/prompts")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_prompt_not_found(client: AsyncClient, db_session):
    """GET /admin/prompts/{name} for non-existent template returns 404."""
    headers = await _get_admin_headers(db_session)
    resp = await client.get("/api/v1/admin/prompts/nonexistent", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_prompt_not_found(client: AsyncClient, db_session):
    """PUT /admin/prompts/{name} for non-existent template returns 404."""
    headers = await _get_admin_headers(db_session)
    resp = await client.put(
        "/api/v1/admin/prompts/nonexistent",
        headers=headers,
        json={"yaml": "system: 'test'", "change_note": "test"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_prompt_lifecycle(client: AsyncClient, db_session):
    """Full CRUD lifecycle: seed → get → list → update → versions → eval."""
    headers = await _get_admin_headers(db_session)

    # 1. No templates yet
    resp = await client.get("/api/v1/admin/prompts", headers=headers)
    assert resp.status_code == 200
    initial_list = resp.json()
    
    if len(initial_list) == 0:
        # Create a template directly via repo to test GET/UPDATE
        from app.repositories.prompt_repo import PromptRepo
        repo = PromptRepo(db_session)
        template = await repo.create(
            name="test_prompt",
            group_name="test_group",
            yaml_content="system: 'test'\ntemperature: 0.5",
            change_note="initial",
        )
        await db_session.commit()
        await db_session.refresh(template)
    else:
        # Templates may already be seeded - use the first one or look for a specific one
        template_name = initial_list[0].get("name", "test_prompt") if isinstance(initial_list[0], dict) else "test_prompt"

    # 2. List should now include templates
    resp = await client.get("/api/v1/admin/prompts", headers=headers)
    assert resp.status_code == 200
    templates = resp.json()
    assert len(templates) > 0

    # Find a template to test with
    target = templates[0]
    target_name = target["name"]

    # 3. Get single template
    resp = await client.get(f"/api/v1/admin/prompts/{target_name}", headers=headers)
    assert resp.status_code == 200
    prompt = resp.json()
    assert prompt["name"] == target_name
    assert "yaml" in prompt
    assert "version" in prompt

    # 4. Update template
    resp = await client.put(
        f"/api/v1/admin/prompts/{target_name}",
        headers=headers,
        json={"yaml": "system: 'updated'\ntemperature: 0.8", "change_note": "version 2"},
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["version"] == target["version"] + 1

    # 5. Get versions
    resp = await client.get(f"/api/v1/admin/prompts/{target_name}/versions", headers=headers)
    assert resp.status_code == 200
    versions = resp.json()
    assert len(versions) >= 2

    # 6. Eval (returns stub)
    resp = await client.post(f"/api/v1/admin/prompts/{target_name}/eval", headers=headers)
    assert resp.status_code == 200
    eval_result = resp.json()
    assert "accuracy" in eval_result