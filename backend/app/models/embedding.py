from sqlalchemy import Column, Integer, ForeignKey
from pgvector.sqlalchemy import VECTOR
from app.database import Base
from app.models.base import TimestampMixin


class DocumentEmbedding(Base, TimestampMixin):
    __tablename__ = "document_embeddings"

    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding = Column(VECTOR(1536), nullable=False)  # OpenAI / text-embedding-3-small