"""Pipeline and review queue Pydantic schemas (B5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Pipeline Run ────────────────────────────────────────────

class StageLog(BaseModel):
    stage: str
    status: str
    message: Optional[str] = None
    timestamp: Optional[datetime] = None


class PipelineRunResponse(BaseModel):
    id: UUID
    input_file: str
    current_stage: str
    status: str
    stage_logs: Optional[List[StageLog]] = None
    question_count: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PipelineRunListResponse(BaseModel):
    items: List[PipelineRunResponse]
    total: int
    page: int
    page_size: int


class PipelineRetryResponse(BaseModel):
    run: PipelineRunResponse
    message: str


# ─── Question Draft / Review ─────────────────────────────────

class QuestionDraftResponse(BaseModel):
    id: UUID
    run_id: Optional[UUID] = None
    raw_ocr: Optional[str] = None
    image_url: Optional[str] = None
    proposed: Optional[Dict[str, Any]] = None
    ai_confidence: Optional[float] = None
    status: str
    reviewer: Optional[str] = None
    reject_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionDraftListResponse(BaseModel):
    items: List[QuestionDraftResponse]
    total: int
    page: int
    page_size: int


class ReviewApproveRequest(BaseModel):
    reviewer: Optional[str] = None


class ReviewRejectRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=2000)
    reviewer: Optional[str] = None


class ReviewEditRequest(BaseModel):
    proposed: Dict[str, Any]
    reviewer: Optional[str] = None


class BulkReviewRequest(BaseModel):
    draft_ids: List[UUID] = Field(..., min_length=1, max_length=200)
    action: str = Field(..., pattern="^(approve|reject)$")
    reject_reason: Optional[str] = None


class BulkReviewResponse(BaseModel):
    approved: int
    rejected: int
    errors: List[Dict[str, Any]] = []