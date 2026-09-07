"""Router for /api/v1/admin/review – Review queue management (B5)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.deps import require_admin
from app.schemas.pipeline import (
    QuestionDraftResponse,
    QuestionDraftListResponse,
    ReviewApproveRequest,
    ReviewRejectRequest,
    ReviewEditRequest,
    BulkReviewRequest,
    BulkReviewResponse,
)
from app.services.pipeline_service import ReviewService

router = APIRouter(prefix="/api/v1/admin/review", tags=["admin-review"])


@router.get("/queue", response_model=QuestionDraftListResponse)
async def list_review_queue(
    status: str = Query("pending", pattern="^(pending|approved|rejected)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """List question drafts in the review queue."""
    service = ReviewService(db)
    items, total = await service.list_drafts(status=status, page=page, page_size=page_size)
    return QuestionDraftListResponse(
        items=[QuestionDraftResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/queue/{draft_id}", response_model=QuestionDraftResponse)
async def get_review_draft(
    draft_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Get a single question draft by ID."""
    service = ReviewService(db)
    draft = await service.get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    return QuestionDraftResponse.model_validate(draft)


@router.post("/queue/{draft_id}/approve", response_model=QuestionDraftResponse)
async def approve_draft(
    draft_id: UUID,
    body: ReviewApproveRequest = ReviewApproveRequest(),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Approve a question draft."""
    service = ReviewService(db)
    try:
        draft = await service.approve(draft_id, body.reviewer or "admin")
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return QuestionDraftResponse.model_validate(draft)


@router.post("/queue/{draft_id}/reject", response_model=QuestionDraftResponse)
async def reject_draft(
    draft_id: UUID,
    body: ReviewRejectRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Reject a question draft with a reason."""
    service = ReviewService(db)
    try:
        draft = await service.reject(draft_id, body.reason, body.reviewer or "admin")
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return QuestionDraftResponse.model_validate(draft)


@router.put("/queue/{draft_id}/edit", response_model=QuestionDraftResponse)
async def edit_draft(
    draft_id: UUID,
    body: ReviewEditRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Edit a question draft's proposed content."""
    service = ReviewService(db)
    try:
        draft = await service.edit(draft_id, body.proposed, body.reviewer or "admin")
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return QuestionDraftResponse.model_validate(draft)


@router.post("/queue/bulk", response_model=BulkReviewResponse)
async def bulk_review(
    body: BulkReviewRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Bulk approve or reject drafts."""
    service = ReviewService(db)
    try:
        result = await service.bulk_review(body.draft_ids, body.action, "admin", body.reject_reason)
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return BulkReviewResponse(**result)