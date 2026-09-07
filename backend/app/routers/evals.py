"""Router for /api/v1/admin/evals – Eval sets, cases, and runs (B5)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.deps import require_admin
from app.schemas.evals import (
    EvalSetCreate,
    EvalSetResponse,
    EvalSetListResponse,
    EvalCaseCreate,
    EvalCaseResponse,
    EvalRunCreate,
    EvalRunResponse,
    EvalRunListResponse,
    EvalRunCasesResponse,
)
from app.services.evals_service import EvalService

router = APIRouter(prefix="/api/v1/admin/evals", tags=["admin-evals"])


# ─── Eval Sets ───────────────────────────────────────────────

@router.get("/sets", response_model=EvalSetListResponse)
async def list_eval_sets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """List all eval sets."""
    service = EvalService(db)
    items, total = await service.list_sets(page=page, page_size=page_size)
    return EvalSetListResponse(
        items=[EvalSetResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/sets/{set_id}", response_model=EvalSetResponse)
async def get_eval_set(
    set_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Get a single eval set by ID."""
    service = EvalService(db)
    eval_set = await service.get_set(set_id)
    if eval_set is None:
        raise HTTPException(status_code=404, detail="Eval set not found")
    return EvalSetResponse.model_validate(eval_set)


@router.post("/sets", response_model=EvalSetResponse, status_code=201)
async def create_eval_set(
    body: EvalSetCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Create a new eval set."""
    service = EvalService(db)
    try:
        eval_set = await service.create_set(body.name, body.description)
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    return EvalSetResponse.model_validate(eval_set)


# ─── Eval Cases ──────────────────────────────────────────────

@router.get("/cases", response_model=list[EvalCaseResponse])
async def list_eval_cases(
    eval_set_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """List all cases in an eval set."""
    service = EvalService(db)
    cases = await service.get_cases_by_set(eval_set_id)
    return [EvalCaseResponse.model_validate(c) for c in cases]


@router.post("/cases", response_model=EvalCaseResponse, status_code=201)
async def add_eval_case(
    body: EvalCaseCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Add a case to an eval set."""
    service = EvalService(db)
    try:
        case = await service.add_case(
            body.eval_set_id,
            body.question_id,
            body.input,
            body.expected_output,
        )
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return EvalCaseResponse.model_validate(case)


# ─── Eval Runs ───────────────────────────────────────────────

@router.get("/runs", response_model=EvalRunListResponse)
async def list_eval_runs(
    eval_set_id: UUID = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """List eval runs, optionally filtered by eval set."""
    service = EvalService(db)
    items, total = await service.list_runs(eval_set_id=eval_set_id, page=page, page_size=page_size)
    return EvalRunListResponse(
        items=[EvalRunResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/runs/{run_id}", response_model=EvalRunResponse)
async def get_eval_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Get a single eval run by ID."""
    service = EvalService(db)
    run = await service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Eval run not found")
    return EvalRunResponse.model_validate(run)


@router.post("/runs", response_model=EvalRunResponse, status_code=201)
async def create_eval_run(
    body: EvalRunCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Start a new eval run."""
    service = EvalService(db)
    try:
        run = await service.create_run(body.eval_set_id, body.prompt_name)
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return EvalRunResponse.model_validate(run)


@router.get("/runs/{run_id}/cases", response_model=EvalRunCasesResponse)
async def get_eval_run_cases(
    run_id: UUID,
    status: str = Query("failed", pattern="^(passed|failed|all)$"),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Get cases for an eval run, filterable by status."""
    service = EvalService(db)
    run = await service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Eval run not found")

    cases = run.case_results or []
    if status != "all":
        cases = [c for c in cases if c.get("status") == status]

    return EvalRunCasesResponse(
        run_id=run_id,
        status=status,
        cases=cases,
    )