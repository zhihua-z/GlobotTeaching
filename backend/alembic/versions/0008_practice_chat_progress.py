"""0008_practice_chat_progress

Create practice_sessions, answer_events, chat_sessions, chat_messages,
study_progress, weekly_reports, user_settings, and mistake_overrides tables (B7-B8).

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-01 17:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Practice ──────────────────────────────────────────────────────
    op.create_table(
        "practice_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject", sa.String(64), nullable=False),
        sa.Column(
            "mode",
            sa.String(32),
            nullable=False,
            server_default=sa.text("'recommend'"),
        ),
        sa.Column("topic_path", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("types", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("count", sa.Integer(), nullable=False, server_default=sa.text("10")),
        sa.Column(
            "status",
            sa.String(16),
            nullable=False,
            server_default=sa.text("'in_progress'"),
        ),
        sa.Column("question_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_practice_sessions_user", "practice_sessions", ["user_id", "status"], unique=False)

    op.create_table(
        "answer_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("practice_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("rubric_breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("time_spent_ms", sa.Integer(), nullable=True),
        sa.Column("flagged", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_answer_events_user", "answer_events", ["user_id", "created_at"], unique=False)
    op.create_index("idx_answer_events_session", "answer_events", ["session_id"], unique=False)
    op.create_index(
        "idx_answer_events_user_question",
        "answer_events",
        ["user_id", "question_id", "is_correct"],
        unique=False,
    )

    # ── Chat ──────────────────────────────────────────────────────────
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject", sa.String(64), nullable=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_chat_sessions_user", "chat_sessions", ["user_id", "updated_at"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("quoted_question_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("quoted_article_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("token_usage", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_chat_messages_session", "chat_messages", ["session_id", "created_at"], unique=False)

    # ── Progress / Reports ────────────────────────────────────────────
    op.create_table(
        "study_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_code", sa.String(64), nullable=False),
        sa.Column("current_chapter_path", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("daily_hours", sa.Float(), nullable=True),
        sa.Column("target_exam_date", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "subject_code", name="uq_study_progress_user_subject"),
    )

    op.create_table(
        "weekly_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("week", sa.String(16), nullable=False),
        sa.Column("markdown", sa.Text(), nullable=True),
        sa.Column("stats", postgresql.JSONB(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "week", name="uq_weekly_reports_user_week"),
    )

    # ── Settings ──────────────────────────────────────────────────────
    op.create_table(
        "user_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("daily_hours", sa.Float(), nullable=True),
        sa.Column("target_exam_date", sa.Date(), nullable=True),
        sa.Column("reminder_times", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("study_prefs", postgresql.JSONB(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("user_settings")
    op.drop_table("weekly_reports")
    op.drop_table("study_progress")
    op.drop_index("idx_chat_messages_session", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("idx_chat_sessions_user", table_name="chat_sessions")
    op.drop_table("chat_sessions")
    op.drop_index("idx_answer_events_user_question", table_name="answer_events")
    op.drop_index("idx_answer_events_session", table_name="answer_events")
    op.drop_index("idx_answer_events_user", table_name="answer_events")
    op.drop_table("answer_events")
    op.drop_index("idx_practice_sessions_user", table_name="practice_sessions")
    op.drop_table("practice_sessions")