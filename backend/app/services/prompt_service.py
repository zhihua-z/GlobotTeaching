"""Prompt template CRUD + eval service."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.repositories.prompt_repo import PromptRepo
from app.models.prompt import PromptTemplate as PromptTemplateModel


class PromptService:
    """Business logic for prompt management."""

    def __init__(self, session: AsyncSession):
        self.repo = PromptRepo(session)

    async def list_all(self) -> list[PromptTemplateModel]:
        return await self.repo.list_all()

    async def get_by_name(self, name: str) -> PromptTemplateModel | None:
        return await self.repo.get_by_name(name)

    async def get_versions(self, name: str) -> list:
        template = await self.repo.get_by_name(name)
        if template is None:
            return []
        return await self.repo.get_versions(template.id)

    async def update(self, name: str, yaml_content: str, change_note: str | None) -> PromptTemplateModel:
        """Update a prompt template, creating a new version."""
        template = await self.repo.get_by_name(name)
        if template is None:
            raise ValueError(f"Prompt template '{name}' not found")
        await self.repo.save_version(template, yaml_content, change_note)
        return template

    async def seed_defaults(self) -> None:
        """Ensure minimal seed prompt templates exist."""
        defaults = [
            ("chat_law_socratic", "chat", "system: \"你是一个法考辅导老师。采用苏格拉底式提问引导学生思考。\"\ntemperature: 0.7\nmax_tokens: 2048\n", "初始版本"),
            ("classify", "pipeline", "system: \"将题目分类到正确的科目和知识点。\"\ntemperature: 0.3\nmax_tokens: 512\n", "初始版本"),
            ("rubric", "pipeline", "system: \"为题目生成评分标准。\"\ntemperature: 0.3\nmax_tokens: 1024\n", "初始版本"),
        ]
        for name, group, yaml, note in defaults:
            existing = await self.repo.get_by_name(name)
            if existing is None:
                await self.repo.create(name, group, yaml, note)

    async def eval_prompt(self, name: str) -> dict:
        """Run evaluation for a prompt (placeholder – returns mock result)."""
        template = await self.repo.get_by_name(name)
        if template is None:
            raise ValueError(f"Prompt template '{name}' not found")
        # TODO(Stage 3): Run actual eval against eval set
        return {"accuracy": 0.92, "recall": 0.88, "message": "eval stub (Stage 3)"}