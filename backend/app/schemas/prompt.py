"""Pydantic schemas for prompt templates."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PromptTemplateResponse(BaseModel):
    """Returned to the client."""
    id: UUID
    name: str
    group: str = Field(validation_alias="group_name")  # alias for frontend compatibility
    yaml: str = Field(validation_alias="yaml_content")
    version: int
    updated_at: datetime
    change_note: Optional[str] = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class PromptTemplateUpdate(BaseModel):
    """Update an existing prompt template."""
    yaml: str
    change_note: Optional[str] = None

    model_config = {"extra": "forbid"}


class PromptTemplateEvalResult(BaseModel):
    """Result of evaluating a prompt template."""
    accuracy: float = 0.0
    recall: float = 0.0
    message: str = "eval not implemented"


class PromptTemplateVersionResponse(BaseModel):
    """A historic version of a prompt template."""
    id: UUID
    version: int
    yaml: str = Field(validation_alias="yaml_content")
    change_note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}