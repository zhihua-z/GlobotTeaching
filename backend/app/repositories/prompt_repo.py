"""Repository for prompt_templates / prompt_template_versions."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.prompt import PromptTemplate as PromptTemplateModel
from app.models.prompt import PromptTemplateVersion


class PromptRepo:
    """Data access for prompt templates (no commit – service manages transaction)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> list[PromptTemplateModel]:
        result = await self.session.execute(
            select(PromptTemplateModel).order_by(PromptTemplateModel.group_name, PromptTemplateModel.name)
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> PromptTemplateModel | None:
        result = await self.session.execute(
            select(PromptTemplateModel).where(PromptTemplateModel.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, group_name: str, yaml_content: str, change_note: str | None = None) -> PromptTemplateModel:
        template = PromptTemplateModel(
            name=name,
            group_name=group_name,
            yaml_content=yaml_content,
            version=1,
            change_note=change_note,
        )
        self.session.add(template)
        # also write version 1
        self.session.add(PromptTemplateVersion(
            template=template,
            version=1,
            yaml_content=yaml_content,
            change_note=change_note,
        ))
        return template

    async def save_version(self, template: PromptTemplateModel, yaml_content: str, change_note: str | None = None) -> None:
        """Append a new version row (called within an already-open transaction)."""
        new_version = template.version + 1
        template.yaml_content = yaml_content
        template.version = new_version
        template.change_note = change_note
        version_row = PromptTemplateVersion(
            template=template,
            version=new_version,
            yaml_content=yaml_content,
            change_note=change_note,
        )
        self.session.add(version_row)

    async def get_versions(self, template_id: UUID) -> list[PromptTemplateVersion]:
        result = await self.session.execute(
            select(PromptTemplateVersion)
            .where(PromptTemplateVersion.template_id == template_id)
            .order_by(PromptTemplateVersion.version.desc())
        )
        return list(result.scalars().all())