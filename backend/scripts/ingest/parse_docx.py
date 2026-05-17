"""
DOCX → list[RawBlock]
用法: python -m scripts.ingest.parse_docx data/raw/2022/paper1.docx > data/drafts/2022_paper1.raw.jsonl
依赖: python-docx
"""
from __future__ import annotations
import json
import sys
import re
from pathlib import Path
from docx import Document

QUESTION_PATTERN = re.compile(r"^\s*(\d{1,3})[.)]\s+(.*)", re.MULTILINE)


def extract_blocks(docx_path: Path) -> list[dict]:
    doc = Document(str(docx_path))
    blocks: list[dict] = []
    page_no = 1
    full_text = "\n".join(p.text for p in doc.paragraphs)
    for m in QUESTION_PATTERN.finditer(full_text):
        blocks.append({
            "q_no": int(m.group(1)),
            "page": page_no,
            "raw_text": m.group(0).strip(),
        })
    return blocks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.ingest.parse_docx <docx_path>", file=sys.stderr)
        sys.exit(1)
    for b in extract_blocks(Path(sys.argv[1])):
        print(json.dumps(b, ensure_ascii=False))