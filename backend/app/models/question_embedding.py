from sqlalchemy import Column, Integer, String, ForeignKey
from pgvector.sqlalchemy import VECTOR
from app.database import Base
from app.models.base import TimestampMixin


class QuestionEmbedding(Base, TimestampMixin):
    __tablename__ = "question_embeddings"

    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    embedding = Column(VECTOR(1024), nullable=False)
    model_name = Column(String(128), nullable=False, default="default")