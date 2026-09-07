"""Eval models (B5)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import ForeignKey, Index, String, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base


class EvalSet(Base):
    __tablename__ = "eval_sets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    case_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    cases: Mapped[List["EvalCase"]] = relationship("EvalCase", back_populates="eval_set")
    runs: Mapped[List["EvalRun"]] = relationship("EvalRun", back_populates="eval_set")


class EvalCase(Base):
    __tablename__ = "eval_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    eval_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("eval_sets.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    input = mapped_column(JSONB, nullable=True)
    expected_output = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    eval_set: Mapped["EvalSet"] = relationship("EvalSet", back_populates="cases")


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    eval_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("eval_sets.id", ondelete="CASCADE"), nullable=False
    )
    prompt_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="running")
    metrics = mapped_column(JSONB, nullable=True)
    case_results = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    eval_set: Mapped["EvalSet"] = relationship("EvalSet", back_populates="runs")


Index("idx_eval_runs_status", EvalRun.status)
Index("idx_eval_cases_set", EvalCase.eval_set_id)