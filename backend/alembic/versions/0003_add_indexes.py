"""Add performance indexes for questions and embeddings tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-16

"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions if not already enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create indexes with IF NOT EXISTS for idempotency
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_curriculum_subject ON questions USING btree (curriculum, subject)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_type ON questions USING btree (type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_difficulty ON questions USING btree (difficulty)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_topic_path_gin ON questions USING gin (topic_path)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_source_origin ON questions USING btree (source_origin)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_stem_trgm ON questions USING gin (stem gin_trgm_ops)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qe_embedding_hnsw "
        "ON question_embeddings USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_questions_curriculum_subject")
    op.execute("DROP INDEX IF EXISTS ix_questions_type")
    op.execute("DROP INDEX IF EXISTS ix_questions_difficulty")
    op.execute("DROP INDEX IF EXISTS ix_questions_topic_path_gin")
    op.execute("DROP INDEX IF EXISTS ix_questions_source_origin")
    op.execute("DROP INDEX IF EXISTS ix_questions_stem_trgm")
    op.execute("DROP INDEX IF EXISTS ix_qe_embedding_hnsw")
