import uuid

from sqlalchemy import Column, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from .engine import BaseORM


class LearningText(BaseORM):
    """ORM модель, описывающая обучающий текст."""

    __tablename__ = "learning_texts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=False, unique=False)
    transcription = Column(Text, nullable=False, unique=False)

    __table_args__ = (Index("learning_text_title_idx", title, postgresql_using="hash"),)
