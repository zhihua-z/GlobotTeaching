"""0007_fsrs_profile

Create fsrs_cards, fsrs_review_logs, profile_events, and profile_snapshots tables (B6).

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-01 17:15:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fsrs_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject", sa.String(64), nullable=False),
        sa.Column("topic_path", postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("stability", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("difficulty", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("lapses", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("state", sa.String(16), nullable=False, server_default=sa.text("'new'")),
        sa.Column("related_question_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "subject", sa.text("topic_path"), name="uq_fsrs_cards_user_subject_topic"),
    )
    op.create_index("idx_fsrs_cards_user_due", "fsrs_cards", ["user_id", "due_at"], unique=False)
    op.create_index("idx_fsrs_cards_user_subject", "fsrs_cards", ["user_id", "subject"], unique=False)

    op.create_table(
        "fsrs_review_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column(
            "card_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("fsrs_cards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rating", sa.String(16), nullable=False),
        sa.Column("elapsed_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("scheduled_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("stability_before", sa.Float(), nullable=True),
        sa.Column("stability_after", sa.Float(), nullable=True),
        sa.Column("difficulty_before", sa.Float(), nullable=True),
        sa.Column("difficulty_after", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_fsrs_review_logs_card", "fsrs_review_logs", ["card_id"], unique=False)

    op.create_table(
        "profile_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("ref_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("subject", sa.String(64), nullable=True),
        sa.Column("topic_path", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("signal", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_profile_events_user_kind", "profile_events", ["user_id", "kind"], unique=False)
    op.create_index("idx_profile_events_user_created", "profile_events", ["user_id", "created_at"], unique=False)

    op.create_table(
        "profile_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level", sa.String(8), nullable=False),
        sa.Column("subject", sa.String(64), nullable=True),
        sa.Column("topic_path", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_profile_snapshots_user_level", "profile_snapshots", ["user_id", "level"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_profile_snapshots_user_level", table_name="profile_snapshots")
    op.drop_table("profile_snapshots")
    op.drop_index("idx_profile_events_user_created", table_name="profile_events")
    op.drop_index("idx_profile_events_user_kind", table_name="profile_events")
    op.drop_table("profile_events")
    op.drop_index("idx_fsrs_review_logs_card", table_name="fsrs_review_logs")
    op.drop_table("fsrs_review_logs")
    op.drop_index("idx_fsrs_cards_user_subject", table_name="fsrs_cards")
    op.drop_index("idx_fsrs_cards_user_due", table_name="fsrs_cards")
    op.drop_table("fsrs_cards")