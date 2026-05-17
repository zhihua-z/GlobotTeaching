#!/usr/bin/env python3
"""Scan questions without embeddings and generate VECTOR(1024) embeddings.

用法:
    python -m scripts.ingest.embed_worker --batch 32

模型维度 1024 (与 question_embeddings 表一致). 使用 OpenAI-compatible API.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

import numpy as np
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database import async_session_factory

# Config — override via env vars
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "deepseek-embedding")  # or compatible model name
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"))
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", os.getenv("OPENAI_API_KEY", "ollama"))
EMBEDDING_DIM = 1024


async def get_embedding(text: str) -> list[float]:
    """Call embedding API to get a 1024-dim vector. Uses aiohttp to avoid OpenAI SDK dep."""
    import aiohttp

    url = f"{EMBEDDING_BASE_URL.rstrip('/')}/embeddings"
    headers = {"Authorization": f"Bearer {EMBEDDING_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": EMBEDDING_MODEL, "input": text[:8192]}  # truncate long stems

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"Embedding API error {resp.status}: {error_text[:500]}")
            data = await resp.json()
            emb = data["data"][0]["embedding"]

    # Ensure exactly 1024 dims
    if len(emb) < EMBEDDING_DIM:
        # Pad with zeros
        emb = emb + [0.0] * (EMBEDDING_DIM - len(emb))
    elif len(emb) > EMBEDDING_DIM:
        emb = emb[:EMBEDDING_DIM]
    return emb


async def process_batch(question_ids: list[int], batch_size: int = 32):
    """Fetch questions without embeddings and generate embeddings in batches."""
    async with async_session_factory() as session:
        for i in range(0, len(question_ids), batch_size):
            batch = question_ids[i:i + batch_size]

            # Fetch stems for this batch
            result = await session.execute(
                text("SELECT id, stem FROM questions WHERE id = ANY(:ids)"),
                {"ids": batch},
            )
            rows = result.fetchall()

            for qid, stem in rows:
                try:
                    emb = await get_embedding(stem)
                    # Insert embedding using pgvector format
                    emb_str = "[" + ",".join(str(x) for x in emb) + "]"
                    await session.execute(
                        text(
                            """
                            INSERT INTO question_embeddings (question_id, embedding, model_name)
                            VALUES (:qid, :emb_vec::vector, :model)
                            ON CONFLICT DO NOTHING
                            """
                        ),
                        {"qid": qid, "emb_vec": emb_str, "model": EMBEDDING_MODEL},
                    )
                    print(f"  ✓ Embedded question {qid} ({len(stem)} chars)")
                except Exception as e:
                    print(f"  ✗ Failed embedding question {qid}: {e}", file=sys.stderr)

            await session.commit()
            print(f"  Batch {i // batch_size + 1}/{(len(question_ids) + batch_size - 1) // batch_size} done ({len(batch)} questions)")


async def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for non-embedded questions")
    parser.add_argument("--batch", type=int, default=32, help="Batch size (default: 32)")
    parser.add_argument("--limit", type=int, default=0, help="Max questions to process (0=all)")
    parser.add_argument("--fake", action="store_true", help="Generate random embeddings (testing only)")
    args = parser.parse_args()

    async with async_session_factory() as session:
        # Find questions without embeddings
        result = await session.execute(
            text(
                """
                SELECT q.id FROM questions q
                WHERE q.deleted_at IS NULL
                AND NOT EXISTS (
                    SELECT 1 FROM question_embeddings qe WHERE qe.question_id = q.id
                )
                ORDER BY q.id
                """
            )
        )
        qids = [row[0] for row in result.fetchall()]

    if args.limit > 0:
        qids = qids[:args.limit]

    if not qids:
        print("All questions already have embeddings. Nothing to do.")
        return

    print(f"Found {len(qids)} questions without embeddings. Processing in batches of {args.batch}...")

    if args.fake:
        # Generate random 1024-dim embeddings for testing
        async with async_session_factory() as session:
            for qid in qids:
                fake_emb = np.random.randn(EMBEDDING_DIM).astype(float).tolist()
                emb_str = "[" + ",".join(str(x) for x in fake_emb) + "]"
                await session.execute(
                    text(
                        "INSERT INTO question_embeddings (question_id, embedding, model_name) VALUES (:qid, :emb_vec::vector, 'fake-1024') ON CONFLICT DO NOTHING"
                    ),
                    {"qid": qid, "emb_vec": emb_str},
                )
            await session.commit()
        print(f"Inserted {len(qids)} fake embeddings (testing).")
    else:
        await process_batch(qids, args.batch)

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())