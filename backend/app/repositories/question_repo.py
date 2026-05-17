from __future__ import annotations
from uuid import UUID
from typing import Optional
from sqlalchemy import select, func, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.question import Question
from app.models.question_embedding import QuestionEmbedding


class QuestionRepo:
    def __init__(self, session: AsyncSession):
        self.s = session

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
        stmt = select(Question)

        if curriculum:
            stmt = stmt.where(Question.curriculum == curriculum)
        if subject:
            stmt = stmt.where(Question.subject == subject)
        if topic:
            stmt = stmt.where(Question.topic_path.contains([topic]))
        if types:
            stmt = stmt.where(Question.type.in_(types))
        if difficulty is not None:
            stmt = stmt.where(Question.difficulty == difficulty)
        if q:
            stmt = stmt.where(Question.stem.ilike(f"%{q}%"))

        # Count total before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.s.execute(count_stmt)).scalar() or 0

        # Ordering
        desc = sort.startswith("-")
        col_name = sort.lstrip("-")
        col = getattr(Question, col_name, Question.created_at)
        order_fn = col.desc() if desc else col.asc()
        stmt = stmt.order_by(order_fn)

        # Pagination
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.s.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def get_by_id(self, question_id: UUID) -> Optional[Question]:
        stmt = select(Question).where(Question.id == question_id)
        result = await self.s.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Question:
        q = Question(**data)
        self.s.add(q)
        await self.s.flush()
        return q

    async def update(self, question_id: UUID, data: dict) -> Optional[Question]:
        stmt = (
            update(Question)
            .where(Question.id == question_id)
            .values(**data)
            .returning(Question)
        )
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none()

    async def delete(self, question_id: UUID, soft: bool = True) -> bool:
        if soft:
            stmt = (
                update(Question)
                .where(Question.id == question_id)
                .values(deleted_at=func.now())
                .returning(Question.id)
            )
        else:
            stmt = (
                delete(Question)
                .where(Question.id == question_id)
                .returning(Question.id)
            )
        result = await self.s.execute(stmt)
        await self.s.flush()
        return result.scalar_one_or_none() is not None

    async def get_by_source_origin(self, source_origin: str) -> Optional[Question]:
        stmt = select(Question).where(Question.source_origin == source_origin)
        result = await self.s.execute(stmt)
        return result.scalar_one_or_none()

    async def get_similar(
        self, question_id: UUID, k: int = 10
    ) -> list[dict]:
        """Find similar questions via embedding cosine similarity."""
        # Get the embedding for the source question
        source_emb = await self.s.execute(
            select(QuestionEmbedding).where(
                QuestionEmbedding.question_id == question_id
            )
        )
        source_emb = source_emb.scalar_one_or_none()
        if source_emb is None:
            return []

        # Use pgvector <=> operator for cosine distance
        stmt = (
            select(
                Question,
                QuestionEmbedding.embedding.cosine_distance(source_emb.embedding).label("distance"),
            )
            .join(QuestionEmbedding, QuestionEmbedding.question_id == Question.id)
            .where(Question.id != question_id)
            .order_by("distance")
            .limit(k)
        )
        result = await self.s.execute(stmt)
        rows = result.all()
        return [
            {
                "id": str(row.Question.id),
                "stem": row.Question.stem[:120],
                "similarity": round(1.0 - float(row.distance), 4),
            }
            for row in rows
        ]

    async def count_in_topic(self, topic: str) -> int:
        stmt = select(func.count()).where(Question.topic_path.contains([topic]))
        result = await self.s.execute(stmt)
        return result.scalar() or 0

    async def difficulty_distribution_in_topic(self, topic: str) -> dict[int, int]:
        stmt = (
            select(Question.difficulty, func.count())
            .where(Question.topic_path.contains([topic]))
            .group_by(Question.difficulty)
        )
        result = await self.s.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def bulk_upsert(
        self, items: list[dict], mode: str = "skip"
    ) -> tuple[int, int, list[dict]]:
        """Bulk upsert questions by source_origin.
        Returns (created, updated, errors)."""
        created = updated = 0
        errors: list[dict] = []

        for item in items:
            try:
                source_origin = item.pop("source_origin", None)
                if not source_origin:
                    errors.append({"error": "missing source_origin", "item": item})
                    continue

                existing = await self.get_by_source_origin(source_origin)
                if existing and mode == "skip":
                    continue
                elif existing and mode == "update":
                    for k, v in item.items():
                        if v is not None:
                            setattr(existing, k, v)
                    updated += 1
                else:
                    self.s.add(Question(source_origin=source_origin, **item))
                    created += 1
            except Exception as e:
                errors.append({"error": str(e), "item": item})

        if created > 0 or updated > 0:
            await self.s.flush()

        return created, updated, errors