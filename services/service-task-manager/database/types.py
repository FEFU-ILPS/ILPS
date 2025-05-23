from enum import Enum


class Status(Enum):
    """Перечисление возможных значений статусов задачи."""

    CREATED = "created"
    STARTED = "started"
    PREPROCESSING = "preprocessing"
    TRANSCRIBING = "transcribing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"
