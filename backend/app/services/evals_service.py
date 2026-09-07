"""Eval sets, cases, and runs business logic (B5)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.evals_repo import EvalRepo
from app.models.evals import EvalSet, EvalCase, EvalRun


class EvalService:
    """Manage eval sets, add cases, and kick off eval runs."""

    def __init__(self, session: AsyncSession):
        self.repo = EvalRepo(session)

    # ─── Sets ────────────────────────────────────────────────

    async def list_sets(self, page: int = 1, page_size: int = 20) -> tuple[list[EvalSet], int]:
        return await self.repo.list_sets(page=page, page_size=page_size)

    async def get_set(self, set_id: UUID) -> EvalSet | None:
        return await self.repo.get_set(set_id)

    async def create_set(self, name: str, description: str | None = None) -> EvalSet:
        existing = await self._get_by_name(name)
        if existing:
            raise ValueError(f"Eval set '{name}' already exists")
        return await self.repo.create_set(name, description)

    async def _get_by_name(self, name: str) -> EvalSet | None:
        # Simple helper: scan list_sets for the name (small-N use case)
        sets, _ = await self.repo.list_sets(page=1, page_size=500)
        for s in sets:
            if s.name == name:
                return s
        return None

    # ─── Cases ───────────────────────────────────────────────

    async def add_case(
        self,
        eval_set_id: UUID,
        question_id: UUID | None = None,
        input_data: dict | None = None,
        expected_output: dict | None = None,
    ) -> EvalCase:
        eval_set = await self.repo.get_set(eval_set_id)
        if eval_set is None:
            raise ValueError(f"Eval set {eval_set_id} not found")
        case = await self.repo.create_case(eval_set_id, question_id, input_data, expected_output)
        return case

    async def get_cases_by_set(self, eval_set_id: UUID) -> list[EvalCase]:
        return await self.repo.get_cases_by_set(eval_set_id)

    # ─── Runs ────────────────────────────────────────────────

    async def list_runs(self, eval_set_id: UUID | None = None, page: int = 1, page_size: int = 20) -> tuple[list[EvalRun], int]:
        return await self.repo.list_runs(eval_set_id=eval_set_id, page=page, page_size=page_size)

    async def get_run(self, run_id: UUID) -> EvalRun | None:
        return await self.repo.get_run(run_id)

    async def create_run(self, eval_set_id: UUID, prompt_name: str | None = None) -> EvalRun:
        eval_set = await self.repo.get_set(eval_set_id)
        if eval_set is None:
            raise ValueError(f"Eval set {eval_set_id} not found")
        return await self.repo.create_run(eval_set_id, prompt_name)