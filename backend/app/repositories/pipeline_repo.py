"""Repository for pipeline_runs and question_drafts (B5)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.pipeline import PipelineRun, QuestionDraft


class PipelineRepo:
    """Data access for pipeline runs (no commit – service manages transaction)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_runs(self, page: int = 1, page_size: int = 20) -> tuple[list[PipelineRun], int]:
        count_q = select(func.count()).select_from(PipelineRun)
        total = (await self.session.execute(count_q)).scalar_one()
        offset = (page - 1) * page_size
        q = select(PipelineRun).order_by(PipelineRun.started_at.desc().nullslast()).offset(offset).limit(page_size)
        result = await self.session.execute(q)
        return list(result.scalars().all()), total

    async def get_run(self, run_id: UUID) -> PipelineRun | None:
        q = select(PipelineRun).where(PipelineRun.id == run_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def create_run(self, input_file: str, stage: str = "upload") -> PipelineRun:
        run = PipelineRun(input_file=input_file, current_stage=stage)
        self.session.add(run)
        return run


class ReviewRepo:
    """Data access for the review queue (question_drafts)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_drafts(
        self, status: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[QuestionDraft], int]:
        base: Select = select(func.count()).select_from(QuestionDraft)
        if status:
            base = base.where(QuestionDraft.status == status)
        total = (await self.session.execute(base)).scalar_one()

        offset = (page - 1) * page_size
        q = select(QuestionDraft).order_by(QuestionDraft.created_at.desc()).offset(offset).limit(page_size)
        if status:
            q = q.where(QuestionDraft.status == status)
        result = await self.session.execute(q)
        return list(result.scalars().all()), total

    async def get_draft(self, draft_id: UUID) -> QuestionDraft | None:
        q = select(QuestionDraft).where(QuestionDraft.id == draft_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def approve_draft(self, draft: QuestionDraft, reviewer: str) -> None:
        draft.status = "approved"
        draft.reviewer = reviewer

    async def reject_draft(self, draft: QuestionDraft, reason: str, reviewer: str) -> None:
        draft.status = "rejected"
        draft.reject_reason = reason
        draft.reviewer = reviewer

    async def edit_draft(self, draft: QuestionDraft, proposed: dict, reviewer: str) -> QuestionDraft:
        draft.proposed = proposed
        draft.reviewer = reviewer
        return draft