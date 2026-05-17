"""create questions and question_embeddings tables

Revision ID: 0001
Revises:
Create Date: 2026-05-15 23:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── questions ────────────────────────────────────────
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("curriculum", sa.String(256), nullable=False),
        sa.Column("subject", sa.String(256), nullable=False),
        sa.Column("topic_path", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("difficulty", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "type",
            sa.Enum(
                "multiple_choice",
                "single_choice",
                "true_false",
                "fill_blank",
                "short_answer",
                "essay",
                "code",
                "matching",
                "ordering",
                name="question_type",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("rubric", postgresql.JSONB(), nullable=True),
        sa.Column("solution", sa.Text(), nullable=True),
        sa.Column("variants", postgresql.ARRAY(sa.UUID()), nullable=False),
        sa.Column("source_origin", sa.String(512), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_questions_curriculum"), "questions", ["curriculum"])
    op.create_index(op.f("ix_questions_subject"), "questions", ["subject"])
    op.create_index(op.f("ix_questions_id"), "questions", ["id"])

    # ── question_embeddings ──────────────────────────────
    op.create_table(
        "question_embeddings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column(
            "embedding",
            postgresql.ARRAY(sa.Float()),
            # We use raw SQL for VECTOR(1024) below
            nullable=False,
        ),
        sa.Column("model_name", sa.String(128), nullable=False, server_default="default"),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_question_embeddings_question_id"),
        "question_embeddings",
        ["question_id"],
    )
    op.create_index(
        op.f("ix_question_embeddings_id"),
        "question_embeddings",
        ["id"],
    )

    # Replace the ARRAY(Float) column with proper VECTOR(1024)
    op.execute(
        """
        ALTER TABLE question_embeddings
        ALTER COLUMN embedding TYPE vector(1024)
        USING embedding::vector(1024)
        """
    )
    op.drop_index("ix_question_embeddings_id", table_name="question_embeddings")
    op.create_index("ix_question_embeddings_id", "question_embeddings", ["id"])


def downgrade() -> None:
    op.drop_table("question_embeddings")

    # Drop the enum type (only if nothing else depends on it)
    op.execute("DROP TYPE IF EXISTS question_type")

    op.drop_table("questions")