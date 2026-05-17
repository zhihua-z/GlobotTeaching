#!/usr/bin/env python3
"""Seed FAKAO curriculum, 8 subjects, and question-type metadata.

Usage:
    python3 backend/scripts/ingest/seed_taxonomy.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from app.database import async_session_factory
from app.models.taxonomy import Curriculum, Subject, QuestionTypeMeta


FAKAO_SUBJECTS = [
    {"code": "civil",     "name": "民法"},
    {"code": "criminal",  "name": "刑法"},
    {"code": "admin",     "name": "行政法与行政诉讼法"},
    {"code": "commercial","name": "商经法"},
    {"code": "intl",      "name": "三国法"},
    {"code": "theory",    "name": "理论法"},
    {"code": "crim-proc", "name": "刑事诉讼法"},
    {"code": "civ-proc",  "name": "民事诉讼法"},
]

QUESTION_TYPES = [
    {"code": "single_choice",   "label_en": "Single Choice",      "label_zh": "单选题",   "requires_options": True,  "requires_rubric": False, "description": "Select one correct answer from options."},
    {"code": "multiple_choice", "label_en": "Multiple Choice",    "label_zh": "多选题",   "requires_options": True,  "requires_rubric": False, "description": "Select one or more correct answers."},
    {"code": "true_false",      "label_en": "True/False",         "label_zh": "判断题",   "requires_options": False, "requires_rubric": False, "description": "Determine if a statement is true or false."},
    {"code": "fill_blank",      "label_en": "Fill in the Blank",  "label_zh": "填空题",   "requires_options": False, "requires_rubric": True,  "description": "Complete the sentence with the correct term(s)."},
    {"code": "short_answer",    "label_en": "Short Answer",       "label_zh": "简答题",   "requires_options": False, "requires_rubric": True,  "description": "Brief written response (a few sentences)."},
    {"code": "essay",           "label_en": "Essay",              "label_zh": "论述题",   "requires_options": False, "requires_rubric": True,  "description": "Extended written response with rubric scoring."},
    {"code": "code",            "label_en": "Code",               "label_zh": "编程题",   "requires_options": False, "requires_rubric": True,  "description": "Write code to solve a problem."},
    {"code": "matching",        "label_en": "Matching",           "label_zh": "匹配题",   "requires_options": True,  "requires_rubric": False, "description": "Match items from two columns."},
    {"code": "ordering",        "label_en": "Ordering",           "label_zh": "排序题",   "requires_options": True,  "requires_rubric": False, "description": "Arrange items in the correct order."},
]


async def seed():
    async with async_session_factory() as session:
        # ── Curriculum: FAKAO ──
        result = await session.execute(select(Curriculum).where(Curriculum.code == "FAKAO"))
        curriculum = result.scalar_one_or_none()
        if not curriculum:
            curriculum = Curriculum(
                code="FAKAO",
                name="中国国家统一法律职业资格考试",
                description="国家统一法律职业资格考试（法考）",
            )
            session.add(curriculum)
            await session.flush()
            print("Created curriculum: FAKAO")
        else:
            print("Curriculum FAKAO already exists")

        # ── Subjects ──
        for sub in FAKAO_SUBJECTS:
            result = await session.execute(
                select(Subject).where(Subject.curriculum_id == curriculum.id, Subject.code == sub["code"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                subject = Subject(
                    curriculum_id=curriculum.id,
                    code=sub["code"],
                    name=sub["name"],
                )
                session.add(subject)
                print(f"  Created subject: {sub['code']} - {sub['name']}")
            else:
                print(f"  Subject already exists: {sub['code']}")

        # ── Question Types ──
        for qt in QUESTION_TYPES:
            result = await session.execute(
                select(QuestionTypeMeta).where(QuestionTypeMeta.code == qt["code"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                qtype = QuestionTypeMeta(
                    code=qt["code"],
                    label_en=qt["label_en"],
                    label_zh=qt["label_zh"],
                    requires_options=qt["requires_options"],
                    requires_rubric=qt["requires_rubric"],
                    description=qt["description"],
                )
                session.add(qtype)
                print(f"  Created question type: {qt['code']} - {qt['label_zh']}")
            else:
                print(f"  Question type already exists: {qt['code']}")

        await session.commit()
        print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())