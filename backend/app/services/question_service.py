from __future__ import annotations
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.question_repo import QuestionRepo
from app.repositories.taxonomy_repo import CurriculumRepo, SubjectRepo
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.models.question import Question


class QuestionService:
    def __init__(self, session: AsyncSession):
        self.repo = QuestionRepo(session)
        self.curriculum_repo = CurriculumRepo(session)
        self.subject_repo = SubjectRepo(session)

    async def search(
        self,
        *,
        curriculum: Optional[str] = None,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        types: Optional[list[str]] = None,
        difficulty: Optional[int] = None,
        q: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort: str = "-created_at",
    ) -> tuple[list[Question], int]:
        return await self.repo.search(
            curriculum=curriculum,
            subject=subject,
            topic=topic,
            types=types,
            difficulty=difficulty,
            q=q,
            page=page,
            page_size=page_size,
            sort=sort,
        )

    async def get_by_id(self, question_id: UUID) -> Optional[Question]:
        return await self.repo.get_by_id(question_id)

    async def create(self, data: QuestionCreate) -> Question:
        return await self.repo.create(data.model_dump())

    async def update(self, question_id: UUID, data: QuestionUpdate) -> Optional[Question]:
        dump = data.model_dump(exclude_unset=True)
        if not dump:
            return await self.repo.get_by_id(question_id)
        return await self.repo.update(question_id, dump)

    async def delete(self, question_id: UUID, soft: bool = True) -> bool:
        return await self.repo.delete(question_id, soft=soft)

    async def bulk_import(
        self, items: list[dict], mode: str = "skip"
    ) -> dict:
        created, updated, errors = await self.repo.bulk_upsert(items, mode=mode)
        return {"created": created, "updated": updated, "errors": errors}

    async def export_jsonl(self, cursor: Optional[str] = None, limit: int = 100) -> list[dict]:
        """Export questions as JSONL-compatible dicts."""
        items, _ = await self.repo.search(page=1, page_size=limit, sort="created_at")
        return [
            {
                "source_origin": q.source_origin,
                "proposed": {
                    "curriculum": q.curriculum,
                    "subject": q.subject,
                    "topic_path": q.topic_path,
                    "type": q.type,
                    "difficulty": q.difficulty,
                    "stem": q.stem,
                    "options": q.options,
                    "answer": q.answer,
                    "rubric": q.rubric,
                    "solution": q.solution,
                },
            }
            for q in items
        ]