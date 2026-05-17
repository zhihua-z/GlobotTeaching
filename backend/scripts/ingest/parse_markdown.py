"""
Markdown → list[RawBlock]
用法: python -m scripts.ingest.parse_markdown data/raw/2022/paper1.md > data/drafts/2022_paper1.raw.jsonl
"""
from __future__ import annotations
import json
import sys
import re
from pathlib import Path

QUESTION_PATTERN = re.compile(r"^###\s*\d{1,3}[.)]\s+.*", re.MULTILINE)


def extract_blocks(md_path: Path) -> list[dict]:
    text = md_path.read_text(encoding="utf-8")
    blocks: list[dict] = []
    current_q_no = 0
    current_text = []
    page_no = 1

    for line in text.splitlines():
        m = QUESTION_PATTERN.match(line)
        if m:
            if current_text:
                blocks.append({
                    "q_no": current_q_no,
                    "page": page_no,
                    "raw_text": "\n".join(current_text).strip(),
                })
            current_q_no += 1
            current_text = [line]
        else:
            current_text.append(line)

    if current_text:
        blocks.append({
            "q_no": current_q_no,
            "page": page_no,
            "raw_text": "\n".join(current_text).strip(),
        })

    return blocks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.ingest.parse_markdown <md_path>", file=sys.stderr)
        sys.exit(1)
    for b in extract_blocks(Path(sys.argv[1])):
        print(json.dumps(b, ensure_ascii=False))