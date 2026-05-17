"""Tests for the questions router."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestQuestionsList:
    async def test_list_empty(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/questions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_create_and_list(self, client: AsyncClient) -> None:
        # Create a question
        payload = {
            "curriculum": "FAKAO",
            "subject": "civil",
            "topic_path": ["民法总则", "民事法律行为"],
            "difficulty": 3,
            "type": "single_choice",
            "stem": "以下哪项属于民事法律行为？",
            "options": [
                {"key": "A", "text": "侵权行为"},
                {"key": "B", "text": "合同行为"},
                {"key": "C", "text": "不当得利"},
                {"key": "D", "text": "无因管理"},
            ],
            "answer": "B",
            "solution": "合同行为是典型的民事法律行为。",
            "source_origin": "FAKAO-2022-civil-Q1",
        }
        create_resp = await client.post("/api/v1/questions", json=payload)
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["curriculum"] == "FAKAO"
        assert created["subject"] == "civil"
        assert created["type"] == "single_choice"
        assert "id" in created

        # List with filter
        list_resp = await client.get("/api/v1/questions?curriculum=FAKAO&subject=civil")
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    async def test_filter_by_type(self, client: AsyncClient) -> None:
        # Create two questions of different types
        for t in ["single_choice", "short_answer"]:
            await client.post("/api/v1/questions", json={
                "curriculum": "FAKAO",
                "subject": "civil",
                "difficulty": 2,
                "type": t,
                "stem": f"Test {t}",
                "answer": "x",
            })

        resp = await client.get("/api/v1/questions?type=single_choice")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["type"] == "single_choice"

    async def test_filter_by_search(self, client: AsyncClient) -> None:
        await client.post("/api/v1/questions", json={
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 2,
            "type": "single_choice",
            "stem": "关于物权法的表述",
            "answer": "A",
        })

        resp = await client.get("/api/v1/questions?q=物权法")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1

    async def test_pagination(self, client: AsyncClient) -> None:
        for i in range(5):
            await client.post("/api/v1/questions", json={
                "curriculum": "FAKAO",
                "subject": "civil",
                "difficulty": 2,
                "type": "single_choice",
                "stem": f"Test question {i}",
                "answer": "A",
            })

        resp = await client.get("/api/v1/questions?page=1&page_size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

        resp2 = await client.get("/api/v1/questions?page=2&page_size=2")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert len(data2["items"]) == 2

    async def test_404_for_missing(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/questions/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404


class TestQuestionCRUD:
    async def test_get_by_id(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/questions", json={
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 3,
            "type": "single_choice",
            "stem": "Test get by ID",
            "answer": "A",
        })
        qid = create_resp.json()["id"]

        resp = await client.get(f"/api/v1/questions/{qid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stem"] == "Test get by ID"

    async def test_update(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/questions", json={
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 2,
            "type": "single_choice",
            "stem": "Original stem",
            "answer": "A",
        })
        qid = create_resp.json()["id"]

        update_resp = await client.patch(f"/api/v1/questions/{qid}", json={
            "stem": "Updated stem",
            "difficulty": 4,
        })
        assert update_resp.status_code == 200
        updated = update_resp.json()
        assert updated["stem"] == "Updated stem"
        assert updated["difficulty"] == 4

    async def test_delete(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/questions", json={
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 2,
            "type": "single_choice",
            "stem": "To be deleted",
            "answer": "A",
        })
        qid = create_resp.json()["id"]

        del_resp = await client.delete(f"/api/v1/questions/{qid}")
        assert del_resp.status_code == 204

        get_resp = await client.get(f"/api/v1/questions/{qid}")
        assert get_resp.status_code == 404

    async def test_create_invalid_type(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/questions", json={
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 2,
            "type": "invalid_type",
            "stem": "Invalid",
        })
        assert resp.status_code == 422


class TestQuestionImport:
    async def test_import_jsonl(self, client: AsyncClient) -> None:
        import io
        jsonl_content = (
            '{"source_origin": "test-1", "curriculum": "FAKAO", '
            '"subject": "civil", "difficulty": 2, "type": "single_choice", '
            '"stem": "Import test 1", "answer": "A"}\n'
            '{"source_origin": "test-2", "curriculum": "FAKAO", '
            '"subject": "criminal", "difficulty": 3, "type": "short_answer", '
            '"stem": "Import test 2", "answer": "B"}\n'
        )
        files = {"file": ("test.jsonl", io.BytesIO(jsonl_content.encode()), "application/jsonl")}
        resp = await client.post("/api/v1/questions/import", files=files)
        assert resp.status_code == 200
        result = resp.json()
        assert result["created"] == 2

        # Verify they're in DB
        list_resp = await client.get("/api/v1/questions?curriculum=FAKAO")
        assert list_resp.json()["total"] == 2

    async def test_import_idempotent(self, client: AsyncClient) -> None:
        import io
        line = (
            '{"source_origin": "dup-test", "curriculum": "FAKAO", '
            '"subject": "civil", "difficulty": 2, "type": "single_choice", '
            '"stem": "Dup", "answer": "A"}\n'
        )
        files = {"file": ("test.jsonl", io.BytesIO(line.encode()), "application/jsonl")}
        resp1 = await client.post("/api/v1/questions/import", files=files)
        assert resp1.json()["created"] == 1

        # Import again
        resp2 = await client.post("/api/v1/questions/import", files=files)
        assert resp2.json()["created"] == 0
        assert resp2.json()["skipped"] == 1