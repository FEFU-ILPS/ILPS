from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from database.types import Status

from .examples import (
    ACCURACY_EXAMPLES,
    COMMENTS_EXAMPLES,
    ID_EXAMPLES,
    MISTAKES_EXAMPLES,
    RESULT_EXAMPLES,
    STATUS_EXAMPLES,
)


class PhoneticMistake(TypedDict):
    """Типизированный словарь для описания фонетической ошибки пользователя."""

    position: int
    reference: str | None
    actual: str | None
    type: str


class BaseSchema(BaseModel):
    """Базовая схема данных."""

    model_config = ConfigDict(from_attributes=True)


class TasksRequest(BaseSchema):
    """Данные, необходимые для получения задач."""

    user_id: UUID = Field(description="Идентификатор пользователя", examples=ID_EXAMPLES)


# *Не используется. Пришлось отказаться из-за особенностей загрузки файлов.
class CreateTaskRequest(BaseSchema):
    """Данные, необходимые для создания задачи."""

    user_id: UUID = Field(description="Идентификатор пользователя", examples=ID_EXAMPLES)
    text_id: UUID = Field(description="Идентификатор текста", examples=ID_EXAMPLES)


class DetailTaskRequest(BaseSchema):
    """Данные, необходимые для получения задач."""

    user_id: UUID = Field(description="Идентификатор пользователя", examples=ID_EXAMPLES)


class CreateTaskResponse(BaseSchema):
    """Данные, отправляемые в ответ на создание задачи."""

    id: UUID = Field(description="Уникальный идентификатор", examples=ID_EXAMPLES)


class TasksResponse(BaseSchema):
    """Данные, отправляемые в ответ на получение задач."""

    id: UUID = Field(description="Уникальный идентификатор", examples=ID_EXAMPLES)
    status: Status = Field(description="Статуст выполнения", examples=STATUS_EXAMPLES)


class DetailTaskResponse(BaseSchema):
    """Данные, отправляемые в ответ на получение информации
    по конкретной задаче.
    """

    id: UUID = Field(description="Уникальный идентификатор", examples=ID_EXAMPLES)
    title: str = Field(description="Название упраженения", max_length=50)
    text_id: UUID = Field(description="Идентификатор текста", examples=ID_EXAMPLES)
    status: Status = Field(description="Статуст выполнения", examples=STATUS_EXAMPLES)
    result: str | None = Field(description="Результат транскрибирования", examples=RESULT_EXAMPLES)
    accuracy: float | None = Field(
        description="Точность произношения", ge=0, le=100, examples=ACCURACY_EXAMPLES
    )
    mistakes: list[PhoneticMistake] | None = Field(
        description="Ошибки произношения", examples=MISTAKES_EXAMPLES
    )
    comment: str | None = Field(description="Комментарий к задаче", examples=COMMENTS_EXAMPLES)
