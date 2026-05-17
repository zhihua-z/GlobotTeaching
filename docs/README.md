# Documentation — Globot Teaching

This directory contains project documentation and Chinese National Judicial Examination (国家统一法律职业资格考试 / 法考) past exam papers in Markdown format.

## Contents

| File | Description |
|------|-------------|
| `题目分析(deepseek)implementation_plan.md` | Implementation plan for parsing and importing exam questions (in Chinese) |
| `2014年法考客观题真题.md` | 2014 National Judicial Examination objective questions (回忆版) |
| `2020年法考客观题真题.md` | 2020 National Judicial Examination objective questions (回忆版) |
| `2021年法考客观题真题.md` | 2021 National Judicial Examination objective questions (回忆版) |
| `2022年法考客观题真题.md` | 2022 National Judicial Examination objective questions (回忆版) |

## Implementation Plan Overview

The file `题目分析(deepseek)implementation_plan.md` outlines a comprehensive plan to:

1. **Parse** the Markdown exam papers into structured JSON data
2. **Import** the parsed data into the PostgreSQL database via the backend API
3. **Build frontend pages** for browsing, analyzing, and managing questions

### Classification Scheme

Each exam question is classified using the existing `questions` table schema:

```
curriculum: "2022年国家统一法律职业资格考试"
├── subject: "试卷一" / "试卷二"
│   ├── topic_path: ["单项选择题"]    → type: single_choice
│   ├── topic_path: ["多项选择题"]    → type: multiple_choice
│   └── topic_path: ["不定项选择题"]  → type: multiple_choice
```

Additional metadata stored in the database:
- `difficulty`: 1-5 (adjustable after import)
- `options`: JSONB with A/B/C/D choices
- `answer`: Ground-truth answer string
- `rubric`: JSONB for grading rules (e.g., indefinite choice markers)
- `source_origin`: Exam year and version identifier

### Planned Implementation Phases

| Phase | Description | Estimated Effort |
|-------|-------------|-----------------|
| Phase 1 | Backend CRUD API for questions | 1-2 days |
| Phase 2 | Markdown → JSON parser scripts | 1-2 days |
| Phase 3 | Frontend pages (browse + admin) | 2-3 days |
| Phase 4 | Data import & testing | 0.5-1 day |
| **Total** | | **4.5-8 days** |

### Data Flow

```
Markdown files  →  Python parser (parse_fakao.py)  →  JSON Lines  →  API import (import_questions.py)  →  PostgreSQL
```

### Markdown Format Structure

The exam papers follow a consistent structure:
- `#` → Curriculum (exam name and year)
- `##` → Subject (试卷一 / 试卷二)
- `###` → Question type section (单项选择题 / 多项选择题 / 不定项选择题)
- `\d+.` → Individual question stem
- `A.` / `B.` / `C.` / `D.` → Answer options
- `**答案：**` → Correct answer marker

## Source Attribution

The exam questions are crowd-sourced recollections (回忆版) from past Chinese National Judicial Examinations. They are used for educational and research purposes within this teaching platform.