from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.repositories.question_repo import QuestionRepo
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/v1/questions", tags=["analysis"])


@router.get("/{question_id}/analysis")
async def get_question_analysis(
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = AnalysisService(session)
    try:
        return await service.get_analysis(question_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Question not found")


@router.get("/{question_id}/similar")
async def get_similar_questions(
    question_id: UUID,
    k: int = 10,
    session: AsyncSession = Depends(get_session),
):
    repo = QuestionRepo(session)
    exists = await repo.get_by_id(question_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Question not found")
    return await repo.get_similar(question_id, k=k)


@router.post("/{question_id}/analysis/refresh")
async def refresh_ai_breakdown(
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = AnalysisService(session)
    return await service.refresh_ai_breakdown(question_id)