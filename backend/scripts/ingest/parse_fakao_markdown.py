#!/usr/bin/env python3
"""Parse 法考 Markdown exam papers → JSON Lines (QuestionDraft).

用法:
    python -m scripts.ingest.parse_fakao_markdown docs/2022年法考客观题真题.md > data/drafts/2022.jsonl

Markdown 格式约定:
    ## 2022年国家统一法律职业资格考试（回忆版）
    ### 试卷一 / 试卷二
    **一、单项选择题。...**   → type: single_choice
    **二、多项选择题。...**   → type: multiple_choice
    **三、不定项选择题。...**  → type: multiple_choice, is_indeterminate: true
    N. 题目题干
        A. 选项A
        B. 选项B
        C. 选项C
        D. 选项D
    **答案：A**  或  **答案：AB**  或  **答案：ABCD**
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

# ——— Subject mapping ——————————————————————————————
# 法考试卷一 and 试卷二 map to different subject combos.
# 试卷一 ≈ 理论法 + 刑法 + 刑诉 + 行政法 + 三国法
# 试卷二 ≈ 民法 + 商经法 + 民诉
PAPER_SUBJECTS: dict[str, str] = {
    "试卷一": "theory",   # 理论法为主（宪法/法理/司法制度）+ 刑法/刑诉/行政法/三国法方向
    "试卷二": "civil",    # 民法为主 + 商经法/民诉方向
}

# Type section patterns → (question_type, is_indeterminate)
SECTION_PATTERNS = [
    (re.compile(r"单项选择"), "single_choice", False),
    (re.compile(r"多项选择"), "multiple_choice", False),
    (re.compile(r"不定项选择"), "multiple_choice", True),
]

QUESTION_RE = re.compile(r"^\s*(\d{1,3})[.)、]\s+(.*)")
OPTION_RE = re.compile(r"^\s*([A-D])[.)、]\s+(.*)")
ANSWER_RE = re.compile(r"\*\*答案[：:]\s*\**(.+?)\**\s*\*\*")
# Some answers are like **答案：A** or **答案：AB** or **答案：A、B** or **答案：**A**
ANSWER_FALLBACK_RE = re.compile(r"答案[：:]\s*([A-D,\s、]+)", re.IGNORECASE)

# Subject hints from headings and context
SUBJECT_HINT_MAP: dict[str, str] = {
    # 试卷一 subjects
    "宪法": "theory",
    "法理": "theory",
    "法制史": "theory",
    "司法制度": "theory",
    "法律职业道德": "theory",
    "刑法": "criminal",
    "刑事诉讼法": "crim_proc",
    "刑诉": "crim_proc",
    "行政法": "admin",
    "行政诉讼法": "admin",
    "国际公法": "intl",
    "国际私法": "intl",
    "国际经济法": "intl",
    "三国法": "intl",
    # 试卷二 subjects
    "民法": "civil",
    "商法": "commercial",
    "经济法": "commercial",
    "知识产权": "commercial",
    "民事诉讼法": "civ_proc",
    "民诉": "civ_proc",
    "仲裁": "civ_proc",
}


def detect_subject_from_text(text: str, paper_name: str) -> str:
    """Try to detect subject from question text keywords. Fall back to paper default."""
    text_lower = text
    for keyword, subject_code in SUBJECT_HINT_MAP.items():
        if keyword in text_lower:
            return subject_code
    return PAPER_SUBJECTS.get(paper_name, "theory")


def parse_answer(raw: str) -> str:
    """Normalize answer string:  A、B、C → A,B,C  or A B C → A,B,C"""
    raw = raw.strip().replace("、", ",").replace(" ", ",")
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return ",".join(p.upper() for p in parts)


def parse_markdown(text: str, fallback_year: Optional[int] = None) -> list[dict]:
    lines = text.split("\n")

    current_paper: Optional[str] = None  # "试卷一" or "试卷二"
    current_year: Optional[str] = None
    current_type: str = "single_choice"
    is_indeterminate: bool = False
    default_subject: str = "theory"

    questions: list[dict] = []

    # Try to detect year from any ## header containing a 4-digit year
    for line in lines:
        if line.startswith("## ") or line.startswith("##"):
            year_match = re.search(r"20\d{2}", line)
            if year_match:
                current_year = year_match.group(0)
                break

    # Use fallback year from filename if no year found in headers
    if current_year is None and fallback_year is not None:
        current_year = str(fallback_year)

    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()

        # Detect paper headers:
        #   ## 试卷一 / ## 试卷二  (2014 format)
        #   ### 试卷一 / ### 试卷二  (2020+ format)
        paper_match = re.search(r"##{1,3}\s*(试卷[一二三四五六])", line_stripped)
        if paper_match:
            paper_name = paper_match.group(1)
            current_paper = paper_name
            # Map paper name: 试卷三 is also 试卷 (some years have 3 papers)
            # Use the primary mapping; fall back to civil for unknown
            mapped = PAPER_SUBJECTS.get(paper_name)
            if mapped:
                default_subject = mapped
            elif paper_name == "试卷三":
                default_subject = "civil"
            i += 1
            continue

        # Detect section headers:
        #   **一、单项选择题...**  (2020+ format)
        #   ### 一、单项选择题...   (2014 format)
        is_section_header = (
            (line_stripped.startswith("**") and "选择题" in line_stripped) or
            (line_stripped.startswith("### ") and "选择题" in line_stripped)
        )
        if is_section_header:
            for pattern, qtype, indeterm in SECTION_PATTERNS:
                if pattern.search(line_stripped):
                    current_type = qtype
                    is_indeterminate = indeterm
                    break
            i += 1
            continue

        # Detect question start: N. stem
        q_match = QUESTION_RE.match(line_stripped)
        if q_match:
            q_num = int(q_match.group(1))
            stem_line = q_match.group(2)

            # Collect full stem (may span multiple lines until first option)
            stem_parts = [stem_line]
            j = i + 1
            answer_found = None
            options: list[dict] = []

            while j < len(lines):
                next_line = lines[j]

                # Check for answer marker
                ans_match = ANSWER_RE.search(next_line) or ANSWER_FALLBACK_RE.search(next_line)
                if ans_match:
                    answer_found = ans_match.group(1).strip()
                    j += 1
                    break

                # Check for option
                opt_match = OPTION_RE.match(next_line)
                if opt_match:
                    break

                # Continue stem (skip empty lines at boundary, but keep content)
                if next_line.strip():
                    stem_parts.append(next_line.strip())
                j += 1

            # Collect options
            while j < len(lines):
                next_line = lines[j]

                # Answer marker in options area
                ans_match = ANSWER_RE.search(next_line) or ANSWER_FALLBACK_RE.search(next_line)
                if ans_match and answer_found is None:
                    answer_found = ans_match.group(1).strip()
                    j += 1
                    break

                opt_match = OPTION_RE.match(next_line)
                if opt_match:
                    options.append({"key": opt_match.group(1).upper(), "text": opt_match.group(2).strip()})
                    j += 1
                    continue

                # If we hit next question or section header, stop
                if QUESTION_RE.match(next_line):
                    break
                if (next_line.startswith("**") and "选择题" in next_line) or \
                   (next_line.startswith("###") and "选择题" in next_line):
                    break
                if next_line.startswith("###") or next_line.startswith("## "):
                    break

                # Try to collect answer if not found yet
                if answer_found is None:
                    ans_match2 = ANSWER_RE.search(next_line) or ANSWER_FALLBACK_RE.search(next_line)
                    if ans_match2:
                        answer_found = ans_match2.group(1).strip()
                        j += 1
                        break

                j += 1

            # Build stem text
            stem = " ".join(filter(None, stem_parts))

            # Parse answer
            answer = parse_answer(answer_found or "")

            # Detect subject from stem text
            detected_subject = detect_subject_from_text(stem, current_paper or "试卷一")

            source_origin = f"FAKAO-{current_year or '????'}-{current_paper or '??'}-Q{q_num}"

            draft = {
                "source_origin": source_origin,
                "raw_text": stem,
                "page": 0,
                "proposed": {
                    "curriculum": "FAKAO",
                    "subject": detected_subject,
                    "topic_path": [current_type.replace("_", " ").title()],
                    "type": current_type,
                    "difficulty": 3,
                    "stem": stem,
                    "options": options or None,
                    "answer": answer,
                    "rubric": {"partial_credit_rule": "all_or_nothing"} if current_type == "multiple_choice" else None,
                    "solution": None,
                    "source_year": int(current_year) if current_year else None,
                    "is_indeterminate": is_indeterminate,
                    "cited_articles": [],
                },
                "review": {"status": "pending", "reviewer": None, "notes": None},
            }
            questions.append(draft)
            i = j
            continue

        i += 1

    return questions


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.ingest.parse_fakao_markdown <path_to_markdown>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Try to extract year from filename (e.g. 2014年法考客观题真题.md → 2014)
    fallback_year = None
    year_in_fname = re.search(r"20\d{2}", path.name)
    if year_in_fname:
        fallback_year = int(year_in_fname.group(0))

    text = path.read_text(encoding="utf-8")
    questions = parse_markdown(text, fallback_year=fallback_year)
    for q in questions:
        print(json.dumps(q, ensure_ascii=False))


if __name__ == "__main__":
    main()