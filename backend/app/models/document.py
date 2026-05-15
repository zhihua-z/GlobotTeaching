from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base
from app.models.base import TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(256), nullable=True)