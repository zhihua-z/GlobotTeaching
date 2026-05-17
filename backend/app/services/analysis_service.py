from __future__ import annotations
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.question_repo import QuestionRepo


class AnalysisService:
    def __init__(self, session: AsyncSession):
        self.repo = QuestionRepo(session)

    async def get_analysis(self, question_id: UUID) -> dict:
        """Aggregate analysis data for a question detail page."""
        question = await self.repo.get_by_id(question_id)
        if question is None:
            raise ValueError("Question not found")

        # Get similar questions
        similar = await self.repo.get_similar(question_id, k=10)

        # Get sibling stats from topic_path
        stats = {}
        siblings_in_topic = 0
        difficulty_dist = {}
        if question.topic_path:
            top_topic = question.topic_path[-1] if question.topic_path else None
            if top_topic:
                siblings_in_topic = await self.repo.count_in_topic(top_topic)
                difficulty_dist = await self.repo.difficulty_distribution_in_topic(top_topic)

        # Basic stats
        stem_len = len(question.stem or "")
        option_count = len(question.options or []) if question.options else 0
        estimated_read_time_sec = max(10, stem_len // 15)  # ~200 chars/sec

        stats = {
            "length_chars": stem_len,
            "option_count": option_count,
            "estimated_read_time_sec": estimated_read_time_sec,
        }

        return {
            "question_id": str(question.id),
            "stats": stats,
            "similar": similar,
            "siblings_in_topic": siblings_in_topic,
            "difficulty_distribution_in_topic": difficulty_dist,
            "ai_breakdown": None,  # Will be populated by LLM service in Stage 3
        }

    async def refresh_ai_breakdown(self, question_id: UUID) -> dict:
        """Regenerate AI breakdown for a question."""
        # Placeholder for Stage 3 LLM integration
        return {"summary": "", "key_concepts": [], "common_mistakes": []}