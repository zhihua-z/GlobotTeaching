"""Router for /api/v1/admin/pipeline – Pipeline run management (B5)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.deps import require_admin
from app.schemas.pipeline import PipelineRunResponse, PipelineRunListResponse, PipelineRetryResponse
from app.services.pipeline_service import PipelineService

router = APIRouter(prefix="/api/v1/admin/pipeline", tags=["admin-pipeline"])


@router.get("/runs", response_model=PipelineRunListResponse)
async def list_pipeline_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """List all pipeline runs."""
    service = PipelineService(db)
    items, total = await service.list_runs(page=page, page_size=page_size)
    return PipelineRunListResponse(
        items=[PipelineRunResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/runs/{run_id}", response_model=PipelineRunResponse)
async def get_pipeline_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Get a single pipeline run by ID."""
    service = PipelineService(db)
    run = await service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return PipelineRunResponse.model_validate(run)


@router.post("/runs/{run_id}/retry", response_model=PipelineRetryResponse)
async def retry_pipeline_run(
    run_id: UUID,
    from_stage: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Retry a pipeline run from a specific stage."""
    service = PipelineService(db)
    try:
        run = await service.retry_run(run_id, from_stage)
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    return PipelineRetryResponse(
        run=PipelineRunResponse.model_validate(run),
        message=f"Retrying from stage '{from_stage}'",
    )


@router.post("/upload", response_model=PipelineRunResponse)
async def upload_pipeline_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Upload a file to start a pipeline run (placeholder – Stage 3)."""
    service = PipelineService(db)
    run = await service.create_run(input_file=file.filename or "unknown")
    await db.commit()
    return PipelineRunResponse.model_validate(run)