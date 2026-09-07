"""SQLAlchemy ORM models – imported so Alembic can detect them."""

from app.models.base import Base
from app.models.question import Question
from app.models.question_embedding import QuestionEmbedding
from app.models.embedding import DocumentEmbedding
from app.models.document import Document
from app.models.taxonomy import Curriculum, Subject, Topic, QuestionTypeMeta
from app.models.auth import User
from app.models.prompt import PromptTemplate, PromptTemplateVersion
from app.models.pipeline import PipelineRun, QuestionDraft
from app.models.evals import EvalSet, EvalCase, EvalRun
from app.models.fsrs import FSRSCard, FSRSReviewLog
from app.models.profile import ProfileEvent, ProfileSnapshot
from app.models.practice import PracticeSession, AnswerEvent
from app.models.chat import ChatSession, ChatMessage
from app.models.progress import StudyProgress, WeeklyReport, UserSettings

__all__ = [
    "Base",
    "Question",
    "QuestionEmbedding",
    "DocumentEmbedding",
    "Document",
    "Curriculum",
    "Subject",
    "Topic",
    "QuestionTypeMeta",
    "User",
    "PromptTemplate",
    "PromptTemplateVersion",
    "PipelineRun",
    "QuestionDraft",
    "EvalSet",
    "EvalCase",
    "EvalRun",
    "FSRSCard",
    "FSRSReviewLog",
    "ProfileEvent",
    "ProfileSnapshot",
    "PracticeSession",
    "AnswerEvent",
    "ChatSession",
    "ChatMessage",
    "StudyProgress",
    "WeeklyReport",
    "UserSettings",
]
