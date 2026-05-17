"""
Normalize raw text blocks into QuestionDraft JSON Lines.
用法: python -m scripts.ingest.normalize < input.raw.jsonl > output.jsonl
"""
from __future__ import annotations
import json
import sys
import re
from typing import Optional


def normalize_block(block: dict) -> dict:
    """Convert a raw text block into a QuestionDraft."""
    raw_text = block.get("raw_text", "")
    source_origin = block.get("source_origin", f"unknown-q{block.get('q_no', 0)}")

    # Basic cleanup: remove extra whitespace
    stem = re.sub(r"\s+", " ", raw_text).strip()

    return {
        "source_origin": source_origin,
        "raw_text": raw_text,
        "page": block.get("page", 1),
        "proposed": {
            "curriculum": "FAKAO",
            "subject": "unknown",
            "topic_path": [],
            "type": "single_choice",
            "difficulty": 3,
            "stem": stem,
            "options": None,
            "answer": None,
            "rubric": None,
            "solution": None,
        },
        "review": {
            "status": "pending",
            "reviewer": None,
            "notes": None,
        },
    }


if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            block = json.loads(line)
            draft = normalize_block(block)
            print(json.dumps(draft, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": str(e), "raw": line}), file=sys.stderr)