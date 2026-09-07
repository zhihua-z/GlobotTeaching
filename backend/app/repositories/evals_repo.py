"""Repository for eval_sets, eval_cases, and eval_runs (B5)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evals import EvalSet, EvalCase, EvalRun


class EvalRepo:
    """Data access for eval sets, cases, and runs (no commit – service manages transaction)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─── Eval Sets ───────────────────────────────────────────

    async def list_sets(self, page: int = 1, page_size: int = 20) -> tuple[list[EvalSet], int]:
        count_q = select(func.count()).select_from(EvalSet)
        total = (await self.session.execute(count_q)).scalar_one()
        offset = (page - 1) * page_size
        q = select(EvalSet).order_by(EvalSet.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(q)
        return list(result.scalars().all()), total

    async def get_set(self, set_id: UUID) -> EvalSet | None:
        q = select(EvalSet).where(EvalSet.id == set_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def create_set(self, name: str, description: str | None = None) -> EvalSet:
        eval_set = EvalSet(name=name, description=description)
        self.session.add(eval_set)
        return eval_set

    # ─── Eval Cases ──────────────────────────────────────────

    async def create_case(
        self,
        eval_set_id: UUID,
        question_id: UUID | None = None,
        input_data: dict | None = None,
        expected_output: dict | None = None,
    ) -> EvalCase:
        case = EvalCase(
            eval_set_id=eval_set_id,
            question_id=question_id,
            input=input_data,
            expected_output=expected_output,
        )
        self.session.add(case)
        return case

    async def get_cases_by_set(self, eval_set_id: UUID) -> list[EvalCase]:
        q = select(EvalCase).where(EvalCase.eval_set_id == eval_set_id).order_by(EvalCase.created_at)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    # ─── Eval Runs ───────────────────────────────────────────

    async def list_runs(self, eval_set_id: UUID | None = None, page: int = 1, page_size: int = 20) -> tuple[list[EvalRun], int]:
        count_q = select(func.count()).select_from(EvalRun)
        if eval_set_id:
            count_q = count_q.where(EvalRun.eval_set_id == eval_set_id)
        total = (await self.session.execute(count_q)).scalar_one()

        offset = (page - 1) * page_size
        q = select(EvalRun).order_by(EvalRun.started_at.desc()).offset(offset).limit(page_size)
        if eval_set_id:
            q = q.where(EvalRun.eval_set_id == eval_set_id)
        result = await self.session.execute(q)
        return list(result.scalars().all()), total

    async def get_run(self, run_id: UUID) -> EvalRun | None:
        q = select(EvalRun).where(EvalRun.id == run_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def create_run(self, eval_set_id: UUID, prompt_name: str | None = None) -> EvalRun:
        run = EvalRun(eval_set_id=eval_set_id, prompt_name=prompt_name)
        self.session.add(run)
        return run