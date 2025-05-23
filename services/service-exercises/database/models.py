import uuid

from sqlalchemy import ARRAY, CheckConstraint, Column, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from .engine import BaseORM
from .types import ExerciseLang, ExerciseTag


class Exercise(BaseORM):
    """ORM модель для описания обучающего упражнения."""

    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seq_number = Column(Integer, primary_key=True, autoincrement=True)
    difficulty = Column(Integer, nullable=False, default=0)
    title = Column(String(50), nullable=False, default="Обычное упражнение")
    preview_image = Column(String(500), nullable=True, default=None)
    background_image = Column(String(500), nullable=True, default=None)
    text_id = Column(UUID(as_uuid=True), nullable=False)
    lang = Column(Enum(ExerciseLang), nullable=False, default=ExerciseLang.ENGLISH)
    tags = Column(ARRAY(Enum(ExerciseTag)), nullable=False, default=[])

    __table_args__ = (
        CheckConstraint(difficulty >= 0, name="check_difficulty_non_neg"),
        CheckConstraint(seq_number > 0, name="check_seq_number_natural"),
    )
