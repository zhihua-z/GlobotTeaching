from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CurriculumBase(BaseModel):
    code: str = Field(..., description="Unique code, e.g. 'FAKAO'")
    name: str = Field(..., description="Display name, e.g. '中国国家统一法律职业资格考试'")
    description: Optional[str] = None


class CurriculumCreate(CurriculumBase):
    pass


class CurriculumUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CurriculumResponse(CurriculumBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubjectBase(BaseModel):
    curriculum_id: UUID
    code: str = Field(..., description="Subject code, e.g. 'civil', 'criminal'")
    name: str = Field(..., description="Display name, e.g. '民法'")
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SubjectResponse(SubjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TopicBase(BaseModel):
    subject_id: UUID
    parent_id: Optional[UUID] = None
    name: str
    slug: str
    depth: int = Field(ge=0, description="0 = root level under subject")


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
    slug: Optional[str] = None


class TopicResponse(TopicBase):
    id: UUID
    created_at: datetime
    question_count: int = 0

    model_config = {"from_attributes": True}


class QuestionTypeMetaResponse(BaseModel):
    code: str
    label_en: str
    label_zh: str
    requires_options: bool
    requires_rubric: bool
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class QuestionTypeMetaUpdate(BaseModel):
    label_zh: Optional[str] = None
    description: Optional[str] = None