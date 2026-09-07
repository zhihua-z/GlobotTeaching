"""Progress, Reports, and Settings models (B7)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StudyProgress(Base):
    __tablename__ = "study_progress"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    subject_code: Mapped[str] = mapped_column(String(64), nullable=False)
    current_chapter_path: Mapped[Optional[list]] = mapped_column(ARRAY(Text), nullable=True)
    daily_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_exam_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    week: Mapped[str] = mapped_column(String(16), nullable=False)
    markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stats: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    daily_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_exam_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    reminder_times: Mapped[Optional[list]] = mapped_column(ARRAY(Text), nullable=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    study_prefs: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())