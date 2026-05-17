"""Taxonomy endpoints: curricula, subjects, topics, question-types."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.taxonomy import Curriculum, Subject, Topic, QuestionTypeMeta

router = APIRouter(prefix="/api/v1", tags=["taxonomy"])


# ── Curricula ────────────────────────────────────────
@router.get("/curricula")
async def list_curricula(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Curriculum).order_by(Curriculum.code))
    return result.scalars().all()


@router.post("/curricula", status_code=201)
async def create_curriculum(
    code: str, name: str, description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    cur = Curriculum(code=code, name=name, description=description)
    db.add(cur)
    await db.commit()
    await db.refresh(cur)
    return cur


@router.patch("/curricula/{curriculum_id}")
async def update_curriculum(
    curriculum_id: UUID, name: Optional[str] = None, description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Curriculum).where(Curriculum.id == curriculum_id))
    cur = result.scalar_one_or_none()
    if not cur:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    if name is not None:
        cur.name = name
    if description is not None:
        cur.description = description
    await db.commit()
    await db.refresh(cur)
    return cur


@router.delete("/curricula/{curriculum_id}", status_code=204)
async def delete_curriculum(curriculum_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Curriculum).where(Curriculum.id == curriculum_id))
    cur = result.scalar_one_or_none()
    if not cur:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    await db.delete(cur)
    await db.commit()
    return None


# ── Subjects ──────────────────────────────────────────
@router.get("/subjects")
async def list_subjects(
    curriculum_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Subject).order_by(Subject.code)
    if curriculum_id:
        stmt = stmt.where(Subject.curriculum_id == curriculum_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/subjects", status_code=201)
async def create_subject(
    curriculum_id: UUID, code: str, name: str, description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    sub = Subject(curriculum_id=curriculum_id, code=code, name=name, description=description)
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.patch("/subjects/{subject_id}")
async def update_subject(
    subject_id: UUID, name: Optional[str] = None, description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    if name is not None:
        sub.name = name
    if description is not None:
        sub.description = description
    await db.commit()
    await db.refresh(sub)
    return sub


@router.delete("/subjects/{subject_id}", status_code=204)
async def delete_subject(subject_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    await db.delete(sub)
    await db.commit()
    return None


# ── Topics ────────────────────────────────────────────
@router.get("/topics")
async def list_topics(
    subject_id: Optional[UUID] = Query(None),
    parent_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Topic).order_by(Topic.name)
    if subject_id:
        stmt = stmt.where(Topic.subject_id == subject_id)
    if parent_id is not None:
        stmt = stmt.where(Topic.parent_id == parent_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/topics", status_code=201)
async def create_topic(
    subject_id: UUID, name: str, slug: str, depth: int = 0,
    parent_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    topic = Topic(subject_id=subject_id, parent_id=parent_id, name=name, slug=slug, depth=depth)
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


@router.patch("/topics/{topic_id}")
async def update_topic(
    topic_id: UUID, name: Optional[str] = None, slug: Optional[str] = None,
    parent_id: Optional[UUID] = None, depth: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if name is not None:
        topic.name = name
    if slug is not None:
        topic.slug = slug
    if parent_id is not None:
        topic.parent_id = parent_id
    if depth is not None:
        topic.depth = depth
    await db.commit()
    await db.refresh(topic)
    return topic


@router.delete("/topics/{topic_id}", status_code=204)
async def delete_topic(
    topic_id: UUID,
    reassign_to: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    await db.delete(topic)
    await db.commit()
    return None


# ── Question Types ────────────────────────────────────
@router.get("/question-types")
async def list_question_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(QuestionTypeMeta).order_by(QuestionTypeMeta.code))
    return result.scalars().all()


@router.patch("/question-types/{code}")
async def update_question_type(
    code: str, label_zh: Optional[str] = None, description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(QuestionTypeMeta).where(QuestionTypeMeta.code == code))
    qt = result.scalar_one_or_none()
    if not qt:
        raise HTTPException(status_code=404, detail="Question type not found")
    if label_zh is not None:
        qt.label_zh = label_zh
    if description is not None:
        qt.description = description
    await db.commit()
    await db.refresh(qt)
    return qt