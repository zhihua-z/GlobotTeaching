from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.repositories.taxonomy_repo import QuestionTypeMetaRepo
from app.schemas.taxonomy import QuestionTypeMetaResponse, QuestionTypeMetaUpdate

router = APIRouter(prefix="/api/v1/question-types", tags=["question-types"])


@router.get("", response_model=list[QuestionTypeMetaResponse])
async def list_question_types(session: AsyncSession = Depends(get_session)):
    repo = QuestionTypeMetaRepo(session)
    return await repo.list_all()


@router.patch("/{code}", response_model=QuestionTypeMetaResponse)
async def update_question_type(
    code: str,
    data: QuestionTypeMetaUpdate,
    session: AsyncSession = Depends(get_session),
):
    repo = QuestionTypeMetaRepo(session)
    dump = data.model_dump(exclude_unset=True)
    if not dump:
        raise HTTPException(status_code=400, detail="No fields to update")
    obj = await repo.update(code, dump)
    if obj is None:
        raise HTTPException(status_code=404, detail="Question type not found")
    return obj