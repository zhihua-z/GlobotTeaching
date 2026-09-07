"""0005_pipeline_review_evals

Create pipeline_runs and question_drafts tables (B5).

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-31 22:04:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pipeline_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("input_file", sa.String(512), nullable=False),
        sa.Column("current_stage", sa.String(32), nullable=False, server_default=sa.text("'upload'")),
        sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("stage_logs", postgresql.JSONB(), nullable=True),
        sa.Column("question_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_pipeline_runs_status", "pipeline_runs", ["status"], unique=False)

    op.create_table(
        "question_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pipeline_runs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("raw_ocr", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("proposed", postgresql.JSONB(), nullable=True),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("reviewer", sa.String(128), nullable=True),
        sa.Column("reject_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_question_drafts_status", "question_drafts", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_question_drafts_status", table_name="question_drafts")
    op.drop_table("question_drafts")
    op.drop_index("idx_pipeline_runs_status", table_name="pipeline_runs")
    op.drop_table("pipeline_runs")