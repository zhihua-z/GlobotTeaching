"""Prompt template and version ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, unique=True)
    group_name = Column(String(64), nullable=False)
    yaml_content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    change_note = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("PromptTemplateVersion", back_populates="template", order_by="PromptTemplateVersion.version.desc()")


class PromptTemplateVersion(Base):
    __tablename__ = "prompt_template_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    yaml_content = Column(Text, nullable=False)
    change_note = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    template = relationship("PromptTemplate", back_populates="versions")