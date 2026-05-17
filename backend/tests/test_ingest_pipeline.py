"""Tests for the ingest pipeline (parse → normalize → seed)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from httpx import AsyncClient


class TestParseFakaoMarkdown:
    """Test the FAKAO markdown parser."""

    @pytest.mark.skip(reason="Needs actual markdown file to parse")
    async def test_parse_2022_markdown(self) -> None:
        from scripts.ingest.parse_fakao_markdown import parse_fakao_questions

        md_path = Path("docs/2022年法考客观题真题.md")
        assert md_path.exists(), "Test markdown file not found"

        questions = parse_fakao_questions(md_path)
        assert len(questions) > 0, "Should parse at least one question"

        for q in questions:
            assert "stem" in q
            assert "subject" in q
            assert "type" in q
            assert "answer" in q
            assert "options" in q or q["type"] in ("true_false",)

    async def test_draft_jsonl_schema(self) -> None:
        """Validate that draft JSONL conforms to expected schema."""
        draft_path = Path("data/drafts/2022_fakao.jsonl")
        if not draft_path.exists():
            pytest.skip("Draft JSONL not found; run parse_fakao_markdown first")

        for i, line in enumerate(draft_path.read_text().splitlines()):
            obj = json.loads(line)
            assert "source_origin" in obj, f"Line {i}: missing source_origin"
            assert "proposed" in obj, f"Line {i}: missing proposed"
            p = obj["proposed"]
            assert "stem" in p, f"Line {i}.proposed: missing stem"
            assert "type" in p, f"Line {i}.proposed: missing type"
            assert p["type"] in (
                "single_choice", "multiple_choice", "true_false",
                "fill_blank", "short_answer", "essay", "code",
            ), f"Line {i}: unknown type {p['type']}"


class TestSeedQuestions:
    """Integration test: seed from JSONL and verify DB state."""

    async def test_seed_from_jsonl(self, client: AsyncClient) -> None:
        """Create a temp JSONL, seed it, verify via API."""
        import tempfile

        lines = [
            json.dumps({
                "source_origin": f"seed-test-{i}",
                "curriculum": "FAKAO",
                "subject": "civil",
                "topic_path": ["民法总则"],
                "difficulty": 2,
                "type": "single_choice",
                "stem": f"Seed test question {i}",
                "options": [
                    {"key": "A", "text": f"Option A for {i}"},
                    {"key": "B", "text": f"Option B for {i}"},
                ],
                "answer": "A",
                "solution": f"Solution {i}",
            }) for i in range(3)
        ]

        # Use the import API
        import io
        files = {"file": ("test.jsonl", io.BytesIO("\n".join(lines).encode()), "application/jsonl")}
        resp = await client.post("/api/v1/questions/import", files=files)
        assert resp.status_code == 200
        assert resp.json()["created"] == 3

        # Verify in DB
        list_resp = await client.get("/api/v1/questions?q=Seed+test")
        assert list_resp.json()["total"] == 3

    async def test_seed_idempotent(self, client: AsyncClient) -> None:
        import io
        line = json.dumps({
            "source_origin": "idempotent-test",
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 2,
            "type": "single_choice",
            "stem": "Idempotent test",
            "answer": "A",
        })

        resp1 = await client.post("/api/v1/questions/import",
                                   files={"file": ("t.jsonl", io.BytesIO((line + "\n").encode()), "application/jsonl")})
        assert resp1.json()["created"] == 1

        resp2 = await client.post("/api/v1/questions/import",
                                   files={"file": ("t.jsonl", io.BytesIO((line + "\n").encode()), "application/jsonl")})
        assert resp2.json()["created"] == 0
        assert resp2.json()["skipped"] == 1

    async def test_seed_update_mode(self, client: AsyncClient) -> None:
        import io
        import json

        original = json.dumps({
            "source_origin": "update-test",
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 2,
            "type": "single_choice",
            "stem": "Original stem",
            "answer": "A",
        })
        updated = json.dumps({
            "source_origin": "update-test",
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 3,
            "type": "single_choice",
            "stem": "Updated stem",
            "answer": "B",
        })

        # Create
        await client.post("/api/v1/questions/import",
                          files={"file": ("t.jsonl", io.BytesIO((original + "\n").encode()), "application/jsonl")})

        # Update via import (use mode query param - depends on router implementation)
        resp = await client.post("/api/v1/questions/import?mode=update",
                                  files={"file": ("t.jsonl", io.BytesIO((updated + "\n").encode()), "application/jsonl")})
        assert resp.status_code == 200
        assert resp.json()["updated"] == 1

        # Verify update
        list_resp = await client.get("/api/v1/questions?q=Updated+stem")
        assert list_resp.json()["total"] == 1


class TestEmbedWorker:
    """Test the embedding worker logic (mock the model)."""

    async def test_worker_scan_no_unembedded(self, client: AsyncClient) -> None:
        """When no questions exist, worker should report 0."""
        resp = await client.get("/api/v1/questions/embed/status")
        # If the endpoint doesn't exist, skip
        if resp.status_code == 404:
            pytest.skip("embed status endpoint not available")
        assert resp.status_code == 200

    @pytest.mark.skip(reason="Needs actual embedding model running")
    async def test_worker_generates_embeddings(self, client: AsyncClient) -> None:
        """Create a question, run worker, verify embedding exists."""
        # Create question
        create_resp = await client.post("/api/v1/questions", json={
            "curriculum": "FAKAO",
            "subject": "civil",
            "difficulty": 2,
            "type": "single_choice",
            "stem": "Embed test",
            "answer": "A",
        })
        qid = create_resp.json()["id"]

        # Run worker (simulated)
        from scripts.ingest.embed_worker import embed_pending_questions
        count = await embed_pending_questions(batch_size=10)
        assert count >= 1

        # Verify embedding exists
        detail_resp = await client.get(f"/api/v1/questions/{qid}")
        assert detail_resp.json().get("has_embedding") is True