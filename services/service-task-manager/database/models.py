import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, CheckConstraint, Column, DateTime, Enum, Float, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from .engine import BaseORM
from .types import Status


class Task(BaseORM):
    """ORM модель, описывающая общую задачу оценки произношения пользователя."""

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(50), nullable=False, default="Упражнение")
    user_id = Column(UUID(as_uuid=True), nullable=False)
    text_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(Status), nullable=False, default=Status.CREATED)
    result = Column(Text, nullable=True, default=None)
    accuracy = Column(Float(3), nullable=True, default=None)
    mistakes = Column(JSON, nullable=True, default=None)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda _: datetime.now(timezone.utc),
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    comment = Column(Text, nullable=True, default=None)

    __table_args__ = (
        Index("task_text_id_idx", text_id, postgresql_using="hash"),
        Index("task_user_id_idx", user_id, postgresql_using="hash"),
        CheckConstraint((accuracy >= 0.0) & (accuracy <= 100.0), name="check_accuracy"),
    )
