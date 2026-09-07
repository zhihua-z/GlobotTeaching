"""Question CRUD + search + similar + analysis endpoints."""
from __future__ import annotations

import json
import math
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select, func, text, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.question import Question, QuestionType
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionList,
    SimilarQuestion,
    AnalysisResponse,
)

router = APIRouter(prefix="/api/v1", tags=["questions"])


# ── Helper: question → response with has_embedding ──────
async def _to_response(q: Question, db: AsyncSession) -> QuestionResponse:
    has_emb = False
    # check embedding exists (lightweight)
    result = await db.execute(
        text("SELECT 1 FROM question_embeddings WHERE question_id = :qid LIMIT 1"),
        {"qid": q.id},
    )
    has_emb = result.scalar() is not None
    return QuestionResponse(
        id=q.id,
        curriculum=q.curriculum,
        subject=q.subject,
        topic_path=q.topic_path or [],
        difficulty=q.difficulty,
        type=q.type,
        stem=q.stem,
        options=q.options,
        answer=q.answer,
        rubric=q.rubric,
        solution=q.solution,
        variants=q.variants or [],
        source_origin=q.source_origin,
        source_year=q.source_year,
        is_indeterminate=q.is_indeterminate or False,
        cited_articles=q.cited_articles or [],
        created_at=q.created_at,
        updated_at=q.updated_at,
        has_embedding=has_emb,
    )


# ── GET /api/v1/questions ─────────────────────────────
@router.get("/questions", response_model=QuestionList)
async def list_questions(
    curriculum: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    type: Optional[str] = Query(None),  # comma-separated
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    q: Optional[str] = Query(None, description="search stem"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("-created_at"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Question)
    # Only non-deleted
    stmt = stmt.where(Question.deleted_at.is_(None))

    if curriculum:
        stmt = stmt.where(Question.curriculum == curriculum)
    if subject:
        stmt = stmt.where(Question.subject == subject)
    if topic:
        stmt = stmt.where(Question.topic_path.contains([topic]))
    if type:
        types = [t.strip() for t in type.split(",") if t.strip()]
        if types:
            stmt = stmt.where(Question.type.in_([QuestionType(t) for t in types]))
    if difficulty is not None:
        stmt = stmt.where(Question.difficulty == difficulty)
    if q:
        stmt = stmt.where(Question.stem.ilike(f"%{q}%"))

    # Sorting
    sort_col = sort.lstrip("-")
    sort_dir = "desc" if sort.startswith("-") else "asc"
    allowed_sorts = {"created_at", "updated_at", "difficulty", "type", "subject", "id"}
    if sort_col not in allowed_sorts:
        sort_col = "created_at"
    col = getattr(Question, sort_col)
    if sort_dir == "asc":
        stmt = stmt.order_by(func.lower(col).asc() if isinstance(col.type, str) else col.asc())
    else:
        stmt = stmt.order_by(func.lower(col).desc() if isinstance(col.type, str) else col.desc())

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    result = await db.execute(stmt)
    questions = result.scalars().all()

    items = []
    for qq in questions:
        items.append(await _to_response(qq, db))

    return QuestionList(items=items, total=total, page=page, page_size=page_size)


# ── POST /api/v1/questions ────────────────────────────
@router.post("/questions", response_model=QuestionResponse, status_code=201)
async def create_question(data: QuestionCreate, db: AsyncSession = Depends(get_db)):
    question = Question(
        curriculum=data.curriculum,
        subject=data.subject,
        topic_path=data.topic_path,
        difficulty=data.difficulty,
        type=QuestionType(data.type),
        stem=data.stem,
        options=data.options,
        answer=data.answer,
        rubric=data.rubric,
        solution=data.solution,
        variants=data.variants,
        source_origin=data.source_origin,
        source_year=data.source_year,
        is_indeterminate=data.is_indeterminate,
        cited_articles=data.cited_articles,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return await _to_response(question, db)


# ── GET /api/v1/questions/{id} ────────────────────────
@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Question).where(Question.id == question_id, Question.deleted_at.is_(None))
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return await _to_response(question, db)


# ── PATCH /api/v1/questions/{id} ──────────────────────
@router.patch("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int, data: QuestionUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Question).where(Question.id == question_id, Question.deleted_at.is_(None))
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(question, field, value)

    await db.commit()
    await db.refresh(question)
    return await _to_response(question, db)


# ── DELETE /api/v1/questions/{id} (soft delete) ───────
@router.delete("/questions/{question_id}", status_code=204)
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Question).where(Question.id == question_id, Question.deleted_at.is_(None))
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    question.deleted_at = func.now()
    await db.commit()
    return None


# ── GET /api/v1/questions/{id}/similar ────────────────
@router.get("/questions/{question_id}/similar", response_model=list[SimilarQuestion])
async def similar_questions(
    question_id: int,
    k: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    # Get the question's embedding, then cosine similarity search
    emb_result = await db.execute(
        text(
            "SELECT embedding FROM question_embeddings WHERE question_id = :qid LIMIT 1"
        ),
        {"qid": question_id},
    )
    row = emb_result.fetchone()
    if not row:
        return []

    emb = row[0]
    # Convert list to pgvector format string
    emb_str = "[" + ",".join(str(x) for x in emb) + "]"

    # Cosine similarity search
    sim_results = await db.execute(
        text(
            f"""
            SELECT q.id, q.stem, 1 - (qe.embedding <=> :emb_vec::vector) AS similarity
            FROM question_embeddings qe
            JOIN questions q ON q.id = qe.question_id
            WHERE q.deleted_at IS NULL AND q.id != :qid
            ORDER BY qe.embedding <=> :emb_vec::vector
            LIMIT :k
            """
        ),
        {"emb_vec": emb_str, "qid": question_id, "k": k},
    )
    return [
        SimilarQuestion(id=row[0], stem=row[1][:200] if row[1] else "", similarity=round(float(row[2]), 4))
        for row in sim_results.fetchall()
    ]


# ── GET /api/v1/questions/{id}/analysis ───────────────
@router.get("/questions/{question_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Question).where(Question.id == question_id, Question.deleted_at.is_(None))
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    q_response = await _to_response(question, db)

    # Stats
    stem_len = len(question.stem or "")
    opt_count = len(question.options) if isinstance(question.options, list) else 0
    stats = {
        "length_chars": stem_len,
        "option_count": opt_count,
        "estimated_read_time_sec": max(10, stem_len // 15),
    }

    # Siblings count in same topic
    siblings = 0
    diff_dist: dict[str, int] = {}
    if question.topic_path:
        sib_result = await db.execute(
            select(func.count(Question.id)).where(
                Question.topic_path.contains([question.topic_path[-1]]),
                Question.deleted_at.is_(None),
                Question.id != question.id,
            )
        )
        siblings = sib_result.scalar() or 0

        # Difficulty distribution in topic
        dist_result = await db.execute(
            select(Question.difficulty, func.count(Question.id))
            .where(
                Question.topic_path.contains([question.topic_path[-1]]),
                Question.deleted_at.is_(None),
            )
            .group_by(Question.difficulty)
        )
        for d, cnt in dist_result.fetchall():
            diff_dist[str(d)] = cnt

    # Similar questions
    sim_list = await similar_questions(question_id, k=10, db=db)

    return AnalysisResponse(
        question=q_response,
        stats=stats,
        similar=sim_list,
        siblings_in_topic=siblings,
        difficulty_distribution_in_topic=diff_dist,
        ai_breakdown=None,
    )


# ── POST /api/v1/questions/import ─────────────────────
@router.get("/questions/export")
async def export_questions(
    format: str = Query("jsonl"),
    db: AsyncSession = Depends(get_db),
):
    """Export all non-deleted questions as JSONL. Placeholder."""
    result = await db.execute(
        select(Question).where(Question.deleted_at.is_(None))
    )
    questions = result.scalars().all()
    lines = []
    for qq in questions:
        resp = await _to_response(qq, db)
        lines.append(resp.model_dump_json())
    return {"data": "\n".join(lines), "format": format}


# ── POST /api/v1/questions/import ─────────────────────
@router.post("/questions/import", status_code=200)
async def import_questions(
    file: UploadFile = File(...),
    mode: str = Query("skip", description="skip or update"),
    db: AsyncSession = Depends(get_db),
):
    """Import JSONL file. Idempotent by source_origin.

    - mode=skip: skip existing (default)
    - mode=update: update existing rows
    """
    created = 0
    updated = 0
    skipped = 0
    errors: list[dict] = []

    raw = await file.read()
    lines = raw.decode("utf-8").splitlines()

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append({"line": i + 1, "error": f"Invalid JSON: {e}"})
            continue

        source_origin = obj.get("source_origin")
        if not source_origin:
            errors.append({"line": i + 1, "error": "Missing source_origin"})
            continue

        # Check for existing question
        result = await db.execute(
            select(Question).where(
                Question.source_origin == source_origin,
                Question.deleted_at.is_(None),
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            if mode == "skip":
                skipped += 1
                continue
            # mode == update
            update_fields = {k: v for k, v in obj.items() if k != "source_origin"}
            if "type" in update_fields:
                update_fields["type"] = QuestionType(update_fields["type"])
            for field, value in update_fields.items():
                setattr(existing, field, value)
            updated += 1
        else:
            q_type = QuestionType(obj.get("type", "single_choice"))
            question = Question(
                curriculum=obj.get("curriculum", "FAKAO"),
                subject=obj.get("subject", ""),
                topic_path=obj.get("topic_path", []),
                difficulty=obj.get("difficulty", 3),
                type=q_type,
                stem=obj.get("stem", ""),
                options=obj.get("options"),
                answer=obj.get("answer", ""),
                rubric=obj.get("rubric"),
                solution=obj.get("solution"),
                variants=obj.get("variants", []),
                source_origin=source_origin,
                source_year=obj.get("source_year"),
                is_indeterminate=obj.get("is_indeterminate", False),
                cited_articles=obj.get("cited_articles", []),
            )
            db.add(question)
            created += 1

    await db.commit()
    await db.flush()

    return {"created": created, "updated": updated, "skipped": skipped, "errors": errors}


