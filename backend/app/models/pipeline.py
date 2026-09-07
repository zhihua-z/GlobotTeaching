"""Pipeline and review queue models (B5)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import ForeignKey, Index, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    input_file: Mapped[str] = mapped_column(String(512), nullable=False)
    current_stage: Mapped[str] = mapped_column(String(32), default="upload")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    stage_logs = mapped_column(JSONB, nullable=True)
    question_count: Mapped[int] = mapped_column(default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    drafts: Mapped[List["QuestionDraft"]] = relationship("QuestionDraft", back_populates="run")


class QuestionDraft(Base):
    __tablename__ = "question_drafts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("pipeline_runs.id", ondelete="SET NULL"), nullable=True)
    raw_ocr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    proposed = mapped_column(JSONB, nullable=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    reviewer: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    reject_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    run: Mapped[Optional["PipelineRun"]] = relationship("PipelineRun", back_populates="drafts")


Index("idx_pipeline_runs_status", PipelineRun.status)
Index("idx_question_drafts_status", QuestionDraft.status)