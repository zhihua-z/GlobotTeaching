"""add taxonomy tables (curricula, subjects, topics, question_types) + legal_articles + question enhancements

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-17 00:30:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CURRICULUM_ID = "00000000-0000-0000-0000-000000000001"
SUBJECT_IDS = {
    "civil": "10000000-0000-0000-0000-000000000001",
    "criminal": "10000000-0000-0000-0000-000000000002",
    "admin": "10000000-0000-0000-0000-000000000003",
    "commercial": "10000000-0000-0000-0000-000000000004",
    "intl": "10000000-0000-0000-0000-000000000005",
    "theory": "10000000-0000-0000-0000-000000000006",
    "crim_proc": "10000000-0000-0000-0000-000000000007",
    "civ_proc": "10000000-0000-0000-0000-000000000008",
}


def upgrade() -> None:
    # ── curricula ──────────────────────────────────────────
    op.create_table(
        "curricula",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("code", sa.String(64), unique=True, nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── subjects ───────────────────────────────────────────
    op.create_table(
        "subjects",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("curriculum_id", sa.UUID(), sa.ForeignKey("curricula.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("curriculum_id", "code"),
    )

    # ── topics ─────────────────────────────────────────────
    op.create_table(
        "topics",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("subject_id", sa.UUID(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", sa.UUID(), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("slug", sa.String(256), nullable=False),
        sa.Column("depth", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("subject_id", "parent_id", "slug"),
    )

    # ── question_types ─────────────────────────────────────
    op.create_table(
        "question_types",
        sa.Column("code", sa.String(32), primary_key=True),
        sa.Column("label_en", sa.String(128), nullable=False),
        sa.Column("label_zh", sa.String(128), nullable=False),
        sa.Column("requires_options", sa.Boolean(), nullable=False),
        sa.Column("requires_rubric", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    # ── legal_articles ─────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_table(
        "legal_articles",
        sa.Column("article_id", sa.UUID(), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("subject_code", sa.String(64), nullable=False),
        sa.Column("article_number", sa.String(64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("interpretation", sa.Text(), nullable=True),
        sa.Column("is_high_freq", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_legal_articles_subject_code", "legal_articles", ["subject_code"])
    op.create_index("ix_legal_articles_content_trgm", "legal_articles", ["content"], postgresql_using="gin", postgresql_ops={"content": "gin_trgm_ops"})

    # ── question_versions ──────────────────────────────────
    op.create_table(
        "question_versions",
        sa.Column("version_id", sa.UUID(), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("changed_by", sa.String(256), nullable=True),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_question_versions_question_id", "question_versions", ["question_id"])

    # ── Add columns to questions ───────────────────────────
    op.add_column("questions", sa.Column("source_year", sa.SmallInteger(), nullable=True))
    op.add_column("questions", sa.Column("is_indeterminate", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("questions", sa.Column("cited_articles", postgresql.ARRAY(sa.UUID()), nullable=False, server_default="{}"))
    op.add_column("questions", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # ── Indexes for questions ──────────────────────────────
    op.create_index("ix_questions_curriculum_subject", "questions", ["curriculum", "subject"])
    op.create_index("ix_questions_type", "questions", ["type"])
    op.create_index("ix_questions_difficulty", "questions", ["difficulty"])
    op.create_index("ix_questions_topic_path_gin", "questions", ["topic_path"], postgresql_using="gin")
    op.create_index("ix_questions_source_origin", "questions", ["source_origin"])
    op.create_index("ix_questions_stem_trgm", "questions", ["stem"], postgresql_using="gin", postgresql_ops={"stem": "gin_trgm_ops"})
    op.create_index("ix_questions_deleted_at", "questions", ["deleted_at"])

    # ── HNSW index for question_embeddings ─────────────────
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_qe_embedding_hnsw ON question_embeddings USING hnsw (embedding vector_cosine_ops)"
    )

    # ── Seed curriculum: FAKAO ─────────────────────────────
    op.execute(f"""
        INSERT INTO curricula (id, code, name, description)
        VALUES ('{CURRICULUM_ID}', 'FAKAO', '中国国家统一法律职业资格考试', '国家统一法律职业资格考试（法考）个人备考平台')
    """)

    # ── Seed 8 科目 ────────────────────────────────────────
    subjects_seed = [
        (SUBJECT_IDS["civil"], "civil", "民法", "民法"),
        (SUBJECT_IDS["criminal"], "criminal", "刑法", "刑法"),
        (SUBJECT_IDS["admin"], "admin", "行政法", "行政法与行政诉讼法"),
        (SUBJECT_IDS["commercial"], "commercial", "商经法", "商法与经济法"),
        (SUBJECT_IDS["intl"], "intl", "三国法", "国际公法、国际私法、国际经济法"),
        (SUBJECT_IDS["theory"], "theory", "理论法", "法理学、宪法、法制史、司法制度与法律职业道德"),
        (SUBJECT_IDS["crim_proc"], "crim_proc", "刑诉", "刑事诉讼法"),
        (SUBJECT_IDS["civ_proc"], "civ_proc", "民诉", "民事诉讼法（含仲裁制度）"),
    ]
    for sid, code, name, desc in subjects_seed:
        op.execute(f"""
            INSERT INTO subjects (id, curriculum_id, code, name, description)
            VALUES ('{sid}', '{CURRICULUM_ID}', '{code}', '{name}', '{desc}')
        """)

    # ── Seed question_types ────────────────────────────────
    question_types_seed = [
        ("multiple_choice", "Multiple Choice", "多项选择题", True, False, "至少两个正确选项"),
        ("single_choice", "Single Choice", "单项选择题", True, False, "有且仅有一个正确选项"),
        ("true_false", "True/False", "判断题", False, False, "判断正误"),
        ("fill_blank", "Fill in the Blank", "填空题", False, True, "填空作答"),
        ("short_answer", "Short Answer", "简答题", False, True, "简短文字作答"),
        ("essay", "Essay", "论述题/案例分析", False, True, "详细论述或案例分析"),
        ("code", "Code", "编程题", False, True, "编写代码"),
        ("matching", "Matching", "匹配题", True, False, "左右匹配"),
        ("ordering", "Ordering", "排序题", True, False, "给定项排序"),
    ]
    for code, label_en, label_zh, req_opt, req_rub, desc in question_types_seed:
        op.execute(f"""
            INSERT INTO question_types (code, label_en, label_zh, requires_options, requires_rubric, description)
            VALUES ('{code}', '{label_en}', '{label_zh}', {req_opt}, {req_rub}, '{desc}')
        """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_qe_embedding_hnsw")
    op.drop_index("ix_questions_deleted_at", table_name="questions")
    op.drop_index("ix_questions_stem_trgm", table_name="questions", postgresql_using="gin")
    op.drop_index("ix_questions_source_origin", table_name="questions")
    op.drop_index("ix_questions_topic_path_gin", table_name="questions", postgresql_using="gin")
    op.drop_index("ix_questions_difficulty", table_name="questions")
    op.drop_index("ix_questions_type", table_name="questions")
    op.drop_index("ix_questions_curriculum_subject", table_name="questions")
    op.drop_column("questions", "deleted_at")
    op.drop_column("questions", "cited_articles")
    op.drop_column("questions", "is_indeterminate")
    op.drop_column("questions", "source_year")
    op.drop_index("ix_question_versions_question_id", table_name="question_versions")
    op.drop_table("question_versions")
    op.drop_index("ix_legal_articles_content_trgm", table_name="legal_articles", postgresql_using="gin")
    op.drop_index("ix_legal_articles_subject_code", table_name="legal_articles")
    op.drop_table("legal_articles")
    op.drop_table("question_types")
    op.drop_table("topics")
    op.drop_table("subjects")
    op.drop_table("curricula")