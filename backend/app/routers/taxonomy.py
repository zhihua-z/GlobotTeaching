"""Taxonomy endpoints: curricula, subjects, topics, question-types."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.taxonomy import Curriculum, Subject, Topic
from app.schemas.taxonomy import (
    CurriculumCreate,
    CurriculumUpdate,
    CurriculumResponse,
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    TopicCreate,
    TopicUpdate,
    TopicResponse,
)

router = APIRouter(prefix="/api/v1", tags=["taxonomy"])


# ── Helper: check duplicate code ────────────────────
async def _check_dup_curriculum_code(db: AsyncSession, code: str, exclude_id: Optional[UUID] = None) -> None:
    stmt = select(Curriculum).where(Curriculum.code == code)
    if exclude_id:
        stmt = stmt.where(Curriculum.id != exclude_id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Curriculum code already exists")


async def _check_dup_subject_code(db: AsyncSession, curriculum_id: UUID, code: str, exclude_id: Optional[UUID] = None) -> None:
    stmt = select(Subject).where(Subject.curriculum_id == curriculum_id, Subject.code == code)
    if exclude_id:
        stmt = stmt.where(Subject.id != exclude_id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Subject code already exists in this curriculum")


# ── Curricula ────────────────────────────────────────
@router.get("/curricula", response_model=list[CurriculumResponse])
async def list_curricula(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Curriculum).order_by(Curriculum.code))
    return result.scalars().all()


@router.post("/curricula", response_model=CurriculumResponse, status_code=201)
async def create_curriculum(data: CurriculumCreate, db: AsyncSession = Depends(get_db)):
    await _check_dup_curriculum_code(db, data.code)
    cur = Curriculum(code=data.code, name=data.name, description=data.description)
    db.add(cur)
    await db.commit()
    await db.refresh(cur)
    return cur


@router.get("/curricula/{curriculum_id}", response_model=CurriculumResponse)
async def get_curriculum(curriculum_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Curriculum).where(Curriculum.id == curriculum_id))
    cur = result.scalar_one_or_none()
    if not cur:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return cur


@router.patch("/curricula/{curriculum_id}", response_model=CurriculumResponse)
async def update_curriculum(
    curriculum_id: UUID, data: CurriculumUpdate, db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Curriculum).where(Curriculum.id == curriculum_id))
    cur = result.scalar_one_or_none()
    if not cur:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    update_fields = data.model_dump(exclude_unset=True)
    if "code" in update_fields and update_fields["code"] != cur.code:
        await _check_dup_curriculum_code(db, update_fields["code"], exclude_id=curriculum_id)
    for field, value in update_fields.items():
        setattr(cur, field, value)
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
@router.get("/subjects", response_model=list[SubjectResponse])
async def list_subjects(
    curriculum_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Subject).order_by(Subject.code)
    if curriculum_id:
        stmt = stmt.where(Subject.curriculum_id == curriculum_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/subjects", response_model=SubjectResponse, status_code=201)
async def create_subject(data: SubjectCreate, db: AsyncSession = Depends(get_db)):
    await _check_dup_subject_code(db, data.curriculum_id, data.code)
    sub = Subject(
        curriculum_id=data.curriculum_id,
        code=data.code,
        name=data.name,
        description=data.description,
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.patch("/subjects/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: UUID, data: SubjectUpdate, db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(sub, field, value)
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
@router.get("/topics", response_model=list[TopicResponse])
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


@router.post("/topics", response_model=TopicResponse, status_code=201)
async def create_topic(data: TopicCreate, db: AsyncSession = Depends(get_db)):
    topic = Topic(
        subject_id=data.subject_id,
        parent_id=data.parent_id,
        name=data.name,
        slug=data.slug,
        depth=data.depth,
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


@router.patch("/topics/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: UUID, data: TopicUpdate, db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(topic, field, value)
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
    if reassign_to:
        # Reassign child topics
        await db.execute(
            select(Topic).where(Topic.parent_id == topic_id)
        )
        # Use update statement
        from sqlalchemy import update
        await db.execute(
            update(Topic).where(Topic.parent_id == topic_id).values(parent_id=reassign_to)
        )
    await db.delete(topic)
    await db.commit()
    return None