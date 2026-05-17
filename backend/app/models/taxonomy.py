"""Taxonomy models: Curriculum, Subject, Topic, QuestionTypeMeta, LegalArticle, QuestionVersion."""
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, SmallInteger, Boolean, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class Curriculum(Base, TimestampMixin):
    __tablename__ = "curricula"

    # Override TimestampMixin's Integer id with UUID to match migration 0002
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)

    subjects = relationship("Subject", back_populates="curriculum", cascade="all, delete-orphan")


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    # Override TimestampMixin's Integer id with UUID to match migration 0002
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    curriculum_id = Column(UUID(as_uuid=True), ForeignKey("curricula.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(64), nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("curriculum_id", "code"),)

    curriculum = relationship("Curriculum", back_populates="subjects")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(256), nullable=False)
    slug = Column(String(256), nullable=False)
    depth = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("subject_id", "parent_id", "slug"),)

    subject = relationship("Subject", back_populates="topics")
    children = relationship("Topic", backref="parent", remote_side="Topic.id", cascade="all, delete-orphan", single_parent=True)


class QuestionTypeMeta(Base):
    __tablename__ = "question_types"

    code = Column(String(32), primary_key=True)
    label_en = Column(String(128), nullable=False)
    label_zh = Column(String(128), nullable=False)
    requires_options = Column(Boolean, nullable=False)
    requires_rubric = Column(Boolean, nullable=False)
    description = Column(Text, nullable=True)


class LegalArticle(Base):
    __tablename__ = "legal_articles"

    article_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    subject_code = Column(String(64), nullable=False, index=True)
    article_number = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    interpretation = Column(Text, nullable=True)
    is_high_freq = Column(Boolean, nullable=False, default=False)
    effective_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class QuestionVersion(Base):
    __tablename__ = "question_versions"

    version_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot = Column(JSONB, nullable=False)
    changed_by = Column(String(256), nullable=True)
    change_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)