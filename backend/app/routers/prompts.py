"""Router for /api/v1/admin/prompts – Prompt template management (B4)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import require_admin
from app.schemas.prompt import (
    PromptTemplateResponse,
    PromptTemplateUpdate,
    PromptTemplateEvalResult,
    PromptTemplateVersionResponse,
)
from app.services.prompt_service import PromptService

router = APIRouter(prefix="/api/v1/admin/prompts", tags=["admin-prompts"])


@router.get("", response_model=list[PromptTemplateResponse])
async def list_prompts(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """List all prompt templates."""
    service = PromptService(db)
    templates = await service.list_all()
    return [PromptTemplateResponse.model_validate(t) for t in templates]


@router.get("/{name}", response_model=PromptTemplateResponse)
async def get_prompt(
    name: str = Path(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Get a single prompt template by name."""
    service = PromptService(db)
    template = await service.get_by_name(name)
    if template is None:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return PromptTemplateResponse.model_validate(template)


@router.put("/{name}", response_model=PromptTemplateResponse)
async def update_prompt(
    name: str,
    body: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Update a prompt template (creates a new version)."""
    service = PromptService(db)
    try:
        template = await service.update(name, body.yaml, body.change_note)
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    return PromptTemplateResponse.model_validate(template)


@router.get("/{name}/versions", response_model=list[PromptTemplateVersionResponse])
async def list_prompt_versions(
    name: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """List all versions of a prompt template."""
    service = PromptService(db)
    versions = await service.get_versions(name)
    return [PromptTemplateVersionResponse.model_validate(v) for v in versions]


@router.post("/{name}/eval", response_model=PromptTemplateEvalResult)
async def eval_prompt(
    name: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Evaluate a prompt template (placeholder – Stage 3)."""
    service = PromptService(db)
    try:
        result = await service.eval_prompt(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return PromptTemplateEvalResult(**result)