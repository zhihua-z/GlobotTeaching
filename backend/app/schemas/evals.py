"""Eval Pydantic schemas (B5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Eval Set ────────────────────────────────────────────────

class EvalSetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class EvalSetResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    case_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EvalSetListResponse(BaseModel):
    items: List[EvalSetResponse]
    total: int
    page: int
    page_size: int


# ─── Eval Case ───────────────────────────────────────────────

class EvalCaseCreate(BaseModel):
    eval_set_id: UUID
    question_id: Optional[UUID] = None
    input: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None


class EvalCaseResponse(BaseModel):
    id: UUID
    eval_set_id: UUID
    question_id: Optional[UUID] = None
    input: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Eval Run ────────────────────────────────────────────────

class EvalRunCreate(BaseModel):
    eval_set_id: UUID
    prompt_name: Optional[str] = None


class EvalRunResponse(BaseModel):
    id: UUID
    eval_set_id: UUID
    prompt_name: Optional[str] = None
    status: str
    metrics: Optional[Dict[str, Any]] = None
    case_results: Optional[List[Dict[str, Any]]] = None
    started_at: datetime
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EvalRunListResponse(BaseModel):
    items: List[EvalRunResponse]
    total: int
    page: int
    page_size: int


class EvalRunCasesResponse(BaseModel):
    run_id: UUID
    status: str
    cases: Optional[List[Dict[str, Any]]] = None