"""Tests for taxonomy (curricula, subjects, topics, question-types) routers."""

from __future__ import annotations

from httpx import AsyncClient


class TestCurricula:
    async def test_list_curricula(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/curricula")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_create_curriculum(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/curricula", json={
            "code": "TEST",
            "name": "Test Curriculum",
            "description": "A test curriculum",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == "TEST"
        assert data["name"] == "Test Curriculum"
        assert "id" in data

        # List should include it
        list_resp = await client.get("/api/v1/curricula")
        codes = [c["code"] for c in list_resp.json()]
        assert "TEST" in codes

    async def test_create_duplicate_code(self, client: AsyncClient) -> None:
        await client.post("/api/v1/curricula", json={
            "code": "DUP", "name": "First",
        })
        resp = await client.post("/api/v1/curricula", json={
            "code": "DUP", "name": "Second",
        })
        assert resp.status_code == 409

    async def test_update_curriculum(self, client: AsyncClient) -> None:
        create = await client.post("/api/v1/curricula", json={
            "code": "UPDATE", "name": "Before",
        })
        cid = create.json()["id"]

        resp = await client.patch(f"/api/v1/curricula/{cid}", json={
            "name": "After",
            "description": "Updated desc",
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "After"

    async def test_delete_curriculum(self, client: AsyncClient) -> None:
        create = await client.post("/api/v1/curricula", json={
            "code": "DEL", "name": "Delete me",
        })
        cid = create.json()["id"]

        del_resp = await client.delete(f"/api/v1/curricula/{cid}")
        assert del_resp.status_code == 204

        get_resp = await client.get(f"/api/v1/curricula/{cid}")
        assert get_resp.status_code == 404


class TestSubjects:
    async def _create_curriculum(self, client: AsyncClient, code: str = "SUBJ-TEST") -> str:
        resp = await client.post("/api/v1/curricula", json={
            "code": code, "name": code,
        })
        return resp.json()["id"]

    async def test_list_empty_for_curriculum(self, client: AsyncClient) -> None:
        cid = await self._create_curriculum(client, "EMPTY")
        resp = await client.get(f"/api/v1/subjects?curriculum_id={cid}")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_create_subject(self, client: AsyncClient) -> None:
        cid = await self._create_curriculum(client)
        resp = await client.post("/api/v1/subjects", json={
            "curriculum_id": cid,
            "code": "TEST",
            "name": "Test Subject",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == "TEST"
        assert data["curriculum_id"] == cid

    async def test_delete_curriculum_cascades(self, client: AsyncClient) -> None:
        cid = await self._create_curriculum(client, "CASCADE")
        await client.post("/api/v1/subjects", json={
            "curriculum_id": cid,
            "code": "C1",
            "name": "Child",
        })
        # Delete the curriculum
        await client.delete(f"/api/v1/curricula/{cid}")
        # Subjects should be gone
        resp = await client.get(f"/api/v1/subjects?curriculum_id={cid}")
        assert resp.json() == []


class TestQuestionTypes:
    async def test_list_question_types(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/question-types")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # Should have common types
        codes = [t["code"] for t in data]
        assert "single_choice" in codes
        assert "multiple_choice" in codes
        assert "short_answer" in codes

    async def test_update_question_type_label(self, client: AsyncClient) -> None:
        resp = await client.patch("/api/v1/question-types/single_choice", json={
            "label_zh": "单选题",
        })
        assert resp.status_code == 200
        assert resp.json()["label_zh"] == "单选题"

    async def test_delete_not_allowed(self, client: AsyncClient) -> None:
        # Assuming POST / DELETE on question-types returns 405
        resp = await client.post("/api/v1/question-types", json={
            "code": "new_type",
            "label_en": "New Type",
            "label_zh": "新题型",
        })
        assert resp.status_code == 405