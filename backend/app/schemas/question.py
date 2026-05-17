from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CODE = "code"
    MATCHING = "matching"
    ORDERING = "ordering"


# ──────────────────────────────────────────────
# Question Schemas
# ──────────────────────────────────────────────


class QuestionBase(BaseModel):
    curriculum: str = Field(default="FAKAO", max_length=256)
    subject: str = Field(default="theory", max_length=256)
    topic_path: list[str] = Field(default_factory=list)
    difficulty: int = Field(default=3, ge=1, le=5)
    type: QuestionType
    stem: str
    options: Optional[dict[str, Any] | list[dict[str, Any]]] = None
    answer: str = ""
    rubric: Optional[dict[str, Any]] = None
    solution: Optional[str] = None
    variants: list[uuid.UUID] = Field(default_factory=list)
    source_origin: Optional[str] = Field(default=None, max_length=512)
    source_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    is_indeterminate: bool = False
    cited_articles: list[uuid.UUID] = Field(default_factory=list)


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    curriculum: Optional[str] = Field(default=None, max_length=256)
    subject: Optional[str] = Field(default=None, max_length=256)
    topic_path: Optional[list[str]] = None
    difficulty: Optional[int] = Field(default=None, ge=1, le=5)
    type: Optional[QuestionType] = None
    stem: Optional[str] = None
    options: Optional[dict[str, Any] | list[dict[str, Any]]] = None
    answer: Optional[str] = None
    rubric: Optional[dict[str, Any]] = None
    solution: Optional[str] = None
    variants: Optional[list[uuid.UUID]] = None
    source_origin: Optional[str] = Field(default=None, max_length=512)
    source_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    is_indeterminate: Optional[bool] = None
    cited_articles: Optional[list[uuid.UUID]] = None


class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    has_embedding: bool = False

    model_config = {"from_attributes": True}


class QuestionList(BaseModel):
    items: list[QuestionResponse]
    total: int
    page: int
    page_size: int


class SimilarQuestion(BaseModel):
    id: int
    stem: str
    similarity: float


class AnalysisResponse(BaseModel):
    question: QuestionResponse
    stats: dict[str, Any] = {}
    similar: list[SimilarQuestion] = Field(default_factory=list)
    siblings_in_topic: int = 0
    difficulty_distribution_in_topic: dict[str, int] = Field(default_factory=dict)
    ai_breakdown: Optional[dict[str, Any]] = None


# ──────────────────────────────────────────────
# Embedding Schemas
# ──────────────────────────────────────────────


class QuestionEmbeddingBase(BaseModel):
    question_id: int
    embedding: list[float] = Field(..., min_length=1024, max_length=1024)
    model_name: str = Field(default="default", max_length=128)


class QuestionEmbeddingCreate(QuestionEmbeddingBase):
    pass


class QuestionEmbeddingResponse(QuestionEmbeddingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}