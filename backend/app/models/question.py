import uuid
from sqlalchemy import Column, Integer, String, Text, Enum, Float, SmallInteger, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.database import Base
from app.models.base import TimestampMixin
import enum


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CODE = "code"
    MATCHING = "matching"
    ORDERING = "ordering"


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    curriculum = Column(String(256), nullable=False, index=True)
    subject = Column(String(256), nullable=False, index=True)
    topic_path = Column(ARRAY(String), nullable=False, default=list)

    difficulty = Column(SmallInteger, nullable=False, default=1)  # 1-5

    type = Column(
        Enum(QuestionType, name="question_type", create_constraint=True),
        nullable=False,
    )

    stem = Column(Text, nullable=False)  # The question body

    options = Column(JSONB, nullable=True)  # For multiple-choice / matching etc.
    answer = Column(Text, nullable=False)  # Ground-truth answer
    rubric = Column(JSONB, nullable=True)  # Grading criteria
    solution = Column(Text, nullable=True)  # Step-by-step explanation

    variants = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)

    source_origin = Column(String(512), nullable=True)
    source_year = Column(SmallInteger, nullable=True)
    is_indeterminate = Column(Boolean, nullable=False, default=False)
    cited_articles = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
