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

    # Questions composite index
    op.create_index(
        "ix_questions_curriculum_subject",
        "questions",
        ["curriculum", "subject"],
        postgresql_using="btree",
    )

    # Type index
    op.create_index(
        "ix_questions_type",
        "questions",
        ["type"],
        postgresql_using="btree",
    )

    # Difficulty index
    op.create_index(
        "ix_questions_difficulty",
        "questions",
        ["difficulty"],
        postgresql_using="btree",
    )

    # GIN index on topic_path array
    op.create_index(
        "ix_questions_topic_path_gin",
        "questions",
        ["topic_path"],
        postgresql_using="gin",
    )

    # Source origin index
    op.create_index(
        "ix_questions_source_origin",
        "questions",
        ["source_origin"],
        postgresql_using="btree",
    )

    # Trigram index on stem for fuzzy search
    op.create_index(
        "ix_questions_stem_trgm",
        "questions",
        ["stem"],
        postgresql_using="gin",
        postgresql_ops={"stem": "gin_trgm_ops"},
    )

    # HNSW index on embeddings for vector similarity search
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qe_embedding_hnsw "
        "ON question_embeddings USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.drop_index("ix_questions_curriculum_subject", table_name="questions")
    op.drop_index("ix_questions_type", table_name="questions")
    op.drop_index("ix_questions_difficulty", table_name="questions")
    op.drop_index("ix_questions_topic_path_gin", table_name="questions")
    op.drop_index("ix_questions_source_origin", table_name="questions")
    op.drop_index("ix_questions_stem_trgm", table_name="questions")
    op.execute("DROP INDEX IF EXISTS ix_qe_embedding_hnsw")