"""
PDF → list[RawBlock]
用法: python -m scripts.ingest.parse_pdf data/raw/2022/paper1.pdf > data/drafts/2022_paper1.raw.jsonl
依赖: pypdf>=4.0 ; 若有扫描件用 pdfplumber + pytesseract
"""
from __future__ import annotations
import json
import sys
import re
from pathlib import Path
from pypdf import PdfReader

QUESTION_PATTERN = re.compile(r"^\s*(\d{1,3})[.)]\s+(.*)", re.MULTILINE)


def extract_blocks(pdf_path: Path) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    blocks: list[dict] = []
    for page_no, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for m in QUESTION_PATTERN.finditer(text):
            blocks.append({
                "q_no": int(m.group(1)),
                "page": page_no,
                "raw_text": m.group(0).strip(),
            })
    return blocks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.ingest.parse_pdf <pdf_path>", file=sys.stderr)
        sys.exit(1)
    for b in extract_blocks(Path(sys.argv[1])):
        print(json.dumps(b, ensure_ascii=False))