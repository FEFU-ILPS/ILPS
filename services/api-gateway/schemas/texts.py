from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .examples.texts import (
    ID_EXAMPLES,
    TITLE_EXAMPLES,
    TRANSCRIPTION_EXAMPLES,
    VALUE_EXAMPLES,
)


class BaseSchema(BaseModel):
    """Базовая схема данных."""

    model_config = ConfigDict(from_attributes=True)


class LearningTextResponse(BaseSchema):
    """Данные, отправляемые в ответ на запрос получения всех текстов."""

    id: UUID = Field(description="Уникальный идентификатор", examples=ID_EXAMPLES)
    title: str = Field(max_length=100, description="Название", examples=TITLE_EXAMPLES)


class DetailLearningTextResponse(BaseSchema):
    """Данные, отправляемые в ответ на запрос получения деталей о тексте."""

    id: UUID = Field(description="Уникальный идентификатор", examples=ID_EXAMPLES)
    title: str = Field(max_length=100, description="Название", examples=TITLE_EXAMPLES)
    value: str = Field(description="Содержание", examples=VALUE_EXAMPLES)
    transcription: str = Field(
        description="Транскрипционная запись", examples=TRANSCRIPTION_EXAMPLES
    )


class CreateLearningTextRequest(BaseSchema):
    """Данные, требующиеся для создания/добавления текста в систему."""

    title: str = Field(max_length=100, description="Название", examples=TITLE_EXAMPLES)
    value: str = Field(description="Содержание", examples=VALUE_EXAMPLES)
    transcription: str = Field(
        description="Транскрипционная запись", examples=TRANSCRIPTION_EXAMPLES
    )


class CreateLearningTextResponse(BaseSchema):
    """Данные, отправляемые в ответ на запрос добавления текста."""

    id: UUID = Field(description="Уникальный идентификатор", examples=ID_EXAMPLES)


class DeleteLearningTextResponse(BaseSchema):
    """Данные, отправляемые в ответ на запрос удаления текста."""

    id: UUID = Field(description="Уникальный идентификатор", examples=ID_EXAMPLES)


class UpdateLearningTextRequest(BaseSchema):
    """Данные, требующиеся для обновления данных о тексте."""

    title: UUID | None = Field(
        description="Уникальный идентификатор", default=None, examples=ID_EXAMPLES
    )
    value: str | None = Field(description="Содержание", examples=VALUE_EXAMPLES)
    transcription: str | None = Field(
        description="Транскрипционная запись", examples=TRANSCRIPTION_EXAMPLES
    )


class UpdateLearningTextResponse(DetailLearningTextResponse):
    """Данные, отправляемые в ответ на запрос обновления данных о тексте."""

    id: UUID = Field(description="Уникальный идентификатор", default=None, examples=ID_EXAMPLES)
    title: str = Field(
        max_length=100, description="Название", default=None, examples=TITLE_EXAMPLES
    )
    value: str = Field(description="Содержание", default=None, examples=VALUE_EXAMPLES)
    transcription: str = Field(
        description="Транскрипционная запись", default=None, examples=TRANSCRIPTION_EXAMPLES
    )
