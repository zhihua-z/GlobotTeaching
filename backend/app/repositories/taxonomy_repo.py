from __future__ import annotations
from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.taxonomy import Curriculum, Subject, Topic, QuestionTypeMeta
from app.models.question import Question


class CurriculumRepo:
    def __init__(self, session: AsyncSession):
        self.s = session

    async def list_all(self) -> Sequence[Curriculum]:
        result = await self.s.execute(select(Curriculum).order_by(Curriculum.code))
        return result.scalars().all()

    async def get_by_id(self, cid: UUID) -> Optional[Curriculum]:
        result = await self.s.execute(select(Curriculum).where(Curriculum.id == cid))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Curriculum]:
        result = await self.s.execute(select(Curriculum).where(Curriculum.code == code))
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Curriculum:
        obj = Curriculum(**data)
        self.s.add(obj)
        await self.s.flush()
        return obj

    async def update(self, cid: UUID, data: dict) -> Optional[Curriculum]:
        stmt = (
            update(Curriculum)
            .where(Curriculum.id == cid)
            .values(**data)
            .returning(Curriculum)
        )
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none()

    async def delete(self, cid: UUID) -> bool:
        stmt = delete(Curriculum).where(Curriculum.id == cid).returning(Curriculum.id)
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none() is not None


class SubjectRepo:
    def __init__(self, session: AsyncSession):
        self.s = session

    async def list_by_curriculum(self, curriculum_id: UUID) -> Sequence[Subject]:
        result = await self.s.execute(
            select(Subject).where(Subject.curriculum_id == curriculum_id).order_by(Subject.code)
        )
        return result.scalars().all()

    async def get_by_id(self, sid: UUID) -> Optional[Subject]:
        result = await self.s.execute(select(Subject).where(Subject.id == sid))
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Subject:
        obj = Subject(**data)
        self.s.add(obj)
        await self.s.flush()
        return obj

    async def update(self, sid: UUID, data: dict) -> Optional[Subject]:
        stmt = (
            update(Subject)
            .where(Subject.id == sid)
            .values(**data)
            .returning(Subject)
        )
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none()

    async def delete(self, sid: UUID) -> bool:
        stmt = delete(Subject).where(Subject.id == sid).returning(Subject.id)
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none() is not None

    async def count_questions(self, subject_code: str) -> int:
        stmt = select(func.count()).where(Question.subject == subject_code)
        result = await self.s.execute(stmt)
        return result.scalar() or 0

    async def delete_or_reassign(self, sid: UUID, reassign_to: Optional[UUID] = None) -> bool:
        """Delete subject. If reassign_to is provided, reassign questions first."""
        subject = await self.get_by_id(sid)
        if subject is None:
            return False

        if reassign_to:
            target = await self.get_by_id(reassign_to)
            if target:
                stmt = (
                    update(Question)
                    .where(Question.subject == subject.code)
                    .values(subject=target.code)
                )
                await self.s.execute(stmt)

        stmt = delete(Subject).where(Subject.id == sid).returning(Subject.id)
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none() is not None


class TopicRepo:
    def __init__(self, session: AsyncSession):
        self.s = session

    async def list_by_subject(self, subject_id: UUID, parent_id: Optional[UUID] = None) -> Sequence[Topic]:
        stmt = select(Topic).where(Topic.subject_id == subject_id)
        if parent_id is not None:
            stmt = stmt.where(Topic.parent_id == parent_id)
        else:
            stmt = stmt.where(Topic.parent_id.is_(None))
        stmt = stmt.order_by(Topic.slug)
        result = await self.s.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, tid: UUID) -> Optional[Topic]:
        result = await self.s.execute(select(Topic).where(Topic.id == tid))
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Topic:
        obj = Topic(**data)
        self.s.add(obj)
        await self.s.flush()
        return obj

    async def update(self, tid: UUID, data: dict) -> Optional[Topic]:
        stmt = (
            update(Topic)
            .where(Topic.id == tid)
            .values(**data)
            .returning(Topic)
        )
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none()

    async def delete(self, tid: UUID) -> bool:
        stmt = delete(Topic).where(Topic.id == tid).returning(Topic.id)
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none() is not None

    async def delete_or_reassign(self, tid: UUID, reassign_to: Optional[UUID] = None) -> bool:
        """Delete topic. If reassign_to is provided, reassign child topics first."""
        topic = await self.get_by_id(tid)
        if topic is None:
            return False

        if reassign_to:
            # Reassign child topics to new parent
            stmt = (
                update(Topic)
                .where(Topic.parent_id == tid)
                .values(parent_id=reassign_to)
            )
            await self.s.execute(stmt)

        stmt = delete(Topic).where(Topic.id == tid).returning(Topic.id)
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none() is not None

    async def count_questions(self, topic_name: str) -> int:
        stmt = select(func.count()).where(Question.topic_path.contains([topic_name]))
        result = await self.s.execute(stmt)
        return result.scalar() or 0


class QuestionTypeMetaRepo:
    def __init__(self, session: AsyncSession):
        self.s = session

    async def list_all(self) -> Sequence[QuestionTypeMeta]:
        result = await self.s.execute(select(QuestionTypeMeta).order_by(QuestionTypeMeta.code))
        return result.scalars().all()

    async def get_by_code(self, code: str) -> Optional[QuestionTypeMeta]:
        result = await self.s.execute(select(QuestionTypeMeta).where(QuestionTypeMeta.code == code))
        return result.scalar_one_or_none()

    async def update(self, code: str, data: dict) -> Optional[QuestionTypeMeta]:
        stmt = (
            update(QuestionTypeMeta)
            .where(QuestionTypeMeta.code == code)
            .values(**data)
            .returning(QuestionTypeMeta)
        )
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none()