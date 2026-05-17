#!/usr/bin/env python3
"""Idempotently seed QuestionDraft JSONL files into the questions table.

幂等键: source_origin. 已存在则按 --mode skip|update 处理.

用法:
    python3 backend/scripts/ingest/seed_questions.py data/drafts/2022.jsonl --mode skip
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Allow running as standalone script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database import async_session_factory
from app.models.question import Question, QuestionType


async def seed_file(path: Path, mode: str = "skip") -> tuple[int, int, list[str]]:
    """Seed a single JSONL file. Returns (created, updated, errors)."""
    created = 0
    updated = 0
    errors: list[str] = []

    if not path.exists():
        return 0, 0, [f"File not found: {path}"]

    lines = path.read_text(encoding="utf-8").strip().splitlines()

    async with async_session_factory() as session:
        for lineno, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {lineno}: invalid JSON: {e}")
                continue

            source_origin = row.get("source_origin")
            if not source_origin:
                errors.append(f"Line {lineno}: missing source_origin")
                continue

            proposed = row.get("proposed", {})
            if not proposed:
                errors.append(f"Line {lineno}: missing proposed block")
                continue

            # Check if question already exists
            stmt = select(Question).where(Question.source_origin == source_origin)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing and mode == "skip":
                continue

            try:
                q_type = QuestionType(proposed["type"])
            except (ValueError, KeyError):
                errors.append(f"Line {lineno}: invalid question type: {proposed.get('type')}")
                continue

            if existing and mode == "update":
                existing.curriculum = proposed.get("curriculum", existing.curriculum)
                existing.subject = proposed.get("subject", existing.subject)
                existing.topic_path = proposed.get("topic_path", existing.topic_path)
                existing.type = q_type
                existing.difficulty = proposed.get("difficulty", existing.difficulty)
                existing.stem = proposed.get("stem", existing.stem)
                existing.options = proposed.get("options")
                existing.answer = proposed.get("answer", existing.answer)
                existing.rubric = proposed.get("rubric")
                existing.solution = proposed.get("solution")
                existing.source_year = proposed.get("source_year")
                existing.is_indeterminate = proposed.get("is_indeterminate", False)
                updated += 1
            else:
                question = Question(
                    source_origin=source_origin,
                    curriculum=proposed.get("curriculum", "FAKAO"),
                    subject=proposed.get("subject", "theory"),
                    topic_path=proposed.get("topic_path", []),
                    type=q_type,
                    difficulty=proposed.get("difficulty", 3),
                    stem=proposed.get("stem", ""),
                    options=proposed.get("options"),
                    answer=proposed.get("answer", ""),
                    rubric=proposed.get("rubric"),
                    solution=proposed.get("solution"),
                    source_year=proposed.get("source_year"),
                    is_indeterminate=proposed.get("is_indeterminate", False),
                )
                session.add(question)
                created += 1

        await session.commit()

    return created, updated, errors


def main():
    ap = argparse.ArgumentParser(description="Seed questions from JSONL draft file")
    ap.add_argument("path", type=Path, help="Path to JSONL file")
    ap.add_argument("--mode", choices=["skip", "update"], default="skip",
                    help="skip: ignore existing; update: overwrite existing")
    args = ap.parse_args()

    created, updated, errors = asyncio.run(seed_file(args.path, args.mode))
    print(f"created={created} updated={updated} errors={len(errors)}")
    for err in errors:
        print(f"  ERROR: {err}", file=sys.stderr)


if __name__ == "__main__":
    main()