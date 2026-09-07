"""Pipeline and review queue business logic (B5)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pipeline_repo import PipelineRepo, ReviewRepo
from app.models.pipeline import PipelineRun, QuestionDraft


class PipelineService:
    """Pipeline run management (upload, retry)."""

    def __init__(self, session: AsyncSession):
        self.repo = PipelineRepo(session)

    async def list_runs(self, page: int = 1, page_size: int = 20) -> tuple[list[PipelineRun], int]:
        return await self.repo.list_runs(page=page, page_size=page_size)

    async def get_run(self, run_id: UUID) -> PipelineRun | None:
        return await self.repo.get_run(run_id)

    async def create_run(self, input_file: str) -> PipelineRun:
        return await self.repo.create_run(input_file)

    async def retry_run(self, run_id: UUID, from_stage: str) -> PipelineRun:
        """Retry a pipeline run from a given stage (placeholder – Stage 3 workers)."""
        run = await self.repo.get_run(run_id)
        if run is None:
            raise ValueError(f"Pipeline run {run_id} not found")
        run.current_stage = from_stage
        run.status = "running"
        run.finished_at = None
        return run


class ReviewService:
    """Review queue management (approve/reject/edit drafts)."""

    def __init__(self, session: AsyncSession):
        self.repo = ReviewRepo(session)

    async def list_drafts(
        self, status: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[QuestionDraft], int]:
        return await self.repo.list_drafts(status=status, page=page, page_size=page_size)

    async def get_draft(self, draft_id: UUID) -> QuestionDraft | None:
        return await self.repo.get_draft(draft_id)

    async def approve(self, draft_id: UUID, reviewer: str) -> QuestionDraft:
        draft = await self.repo.get_draft(draft_id)
        if draft is None:
            raise ValueError(f"Draft {draft_id} not found")
        if draft.status not in ("pending",):
            raise ValueError(f"Draft {draft_id} is not pending (current: {draft.status})")
        await self.repo.approve_draft(draft, reviewer)
        # TODO(Stage 3): Write approved question to `questions` table + create question_versions entry
        return draft

    async def reject(self, draft_id: UUID, reason: str, reviewer: str) -> QuestionDraft:
        draft = await self.repo.get_draft(draft_id)
        if draft is None:
            raise ValueError(f"Draft {draft_id} not found")
        if draft.status not in ("pending",):
            raise ValueError(f"Draft {draft_id} is not pending (current: {draft.status})")
        await self.repo.reject_draft(draft, reason, reviewer)
        return draft

    async def edit(self, draft_id: UUID, proposed: dict, reviewer: str) -> QuestionDraft:
        draft = await self.repo.get_draft(draft_id)
        if draft is None:
            raise ValueError(f"Draft {draft_id} not found")
        return await self.repo.edit_draft(draft, proposed, reviewer)

    async def bulk_review(self, draft_ids: list[UUID], action: str, reviewer: str, reject_reason: Optional[str] = None) -> dict:
        approved = 0
        rejected = 0
        errors: list[dict] = []
        for draft_id in draft_ids:
            try:
                if action == "approve":
                    await self.approve(draft_id, reviewer)
                    approved += 1
                else:
                    await self.reject(draft_id, reject_reason or "Bulk rejected", reviewer)
                    rejected += 1
            except ValueError as e:
                errors.append({"draft_id": str(draft_id), "error": str(e)})
        return {"approved": approved, "rejected": rejected, "errors": errors}