from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from database.types import ExerciseLang, ExerciseTag

from .examples import (
    DIFFICYLTY_EXAMPLES,
    ID_EXAMPLES,
    IMAGE_EXAMPLES,
    LANG_EXAMPLES,
    SEQ_NUMBER_EXAMPLES,
    TAGS_EXAMPLES,
    TITLE_EXAMPLES,
)


class BaseSchema(BaseModel):
    """Базовая схема данных."""

    model_config = ConfigDict(from_attributes=True)


class ExerciseResponse(BaseSchema):
    """Данные, отправляемые в ответ на запрос получения списка упражнений."""

    id: UUID = Field(description="Идентификатор упражнения", examples=ID_EXAMPLES)
    seq_number: int = Field(description="Номер упражнения", gt=0, examples=SEQ_NUMBER_EXAMPLES)
    title: str = Field(description="Название упражнения", max_length=50, examples=TITLE_EXAMPLES)
    difficulty: int = Field(description="Сложность упражнения", ge=0, examples=DIFFICYLTY_EXAMPLES)
    preview_image: str | None = Field(
        description="Изображение превью", default=None, examples=IMAGE_EXAMPLES
    )
    lang: ExerciseLang = Field(description="Язык упражнения", examples=LANG_EXAMPLES)
    tags: list[ExerciseTag] = Field(
        description="Теги упражнения", default=[], examples=TAGS_EXAMPLES
    )


class DetailExerciseResponse(BaseSchema):
    """Данные, отправляемые в ответ на запрос получения деталей об упражнении."""

    id: UUID = Field(description="Идентификатор упражнения", examples=ID_EXAMPLES)
    seq_number: int = Field(description="Номер упражнения", gt=0, examples=SEQ_NUMBER_EXAMPLES)
    title: str = Field(description="Название упражнения", max_length=50, examples=TITLE_EXAMPLES)
    difficulty: int = Field(description="Сложность упражнения", ge=0, examples=DIFFICYLTY_EXAMPLES)
    preview_image: str | None = Field(
        description="Изображение превью", default=None, examples=IMAGE_EXAMPLES
    )
    background_image: str | None = Field(
        description="Изображение фона", default=None, examples=IMAGE_EXAMPLES
    )
    text_id: UUID = Field(description="Идентификатор текста", examples=ID_EXAMPLES)
    lang: ExerciseLang = Field(description="Язык упражнения", examples=LANG_EXAMPLES)
    tags: list[ExerciseTag] = Field(
        description="Теги упражнения", default=[], examples=TAGS_EXAMPLES
    )


class CreateExerciseRequest(BaseSchema):
    """Данные, отправляемые в ответ на запрос добавления нового упражнения."""

    difficulty: int = Field(description="Сложность упражнения", ge=0, examples=DIFFICYLTY_EXAMPLES)
    title: str = Field(
        description="Название упражнения",
        max_length=50,
        default="Обычное упражнение",
        examples=TITLE_EXAMPLES,
    )
    preview_image: str | None = Field(
        description="Изображение превью", default=None, examples=IMAGE_EXAMPLES
    )
    background_image: str | None = Field(
        description="Изображение фона", default=None, examples=IMAGE_EXAMPLES
    )
    text_id: UUID = Field(description="Идентификатор текста", examples=ID_EXAMPLES)
    lang: ExerciseLang = Field(description="Язык упражнения", examples=LANG_EXAMPLES)
    tags: list[ExerciseTag] = Field(
        description="Теги упражнения", default=[], examples=TAGS_EXAMPLES
    )


class CreateExerciseResponse(BaseSchema):
    """Данные, требующиеся для создания/добавления нового упражнения."""

    id: UUID = Field(description="Идентификатор упражнения", examples=ID_EXAMPLES)
    seq_number: int = Field(description="Номер упражнения", gt=0, examples=SEQ_NUMBER_EXAMPLES)


class DeleteExerciseResponse(BaseSchema):
    """Данные, отправляемые в ответ на запрос добавления нового упражнения."""

    id: UUID = Field(description="Идентификатор упражнения", examples=ID_EXAMPLES)
    seq_number: int = Field(description="Номер упражнения", gt=0, examples=SEQ_NUMBER_EXAMPLES)


class UpdateExerciseRequest(BaseSchema):
    """Данные, для обновления информации об упражнении."""

    difficulty: int | None = Field(
        description="Сложность упражнения", ge=0, default=None, examples=DIFFICYLTY_EXAMPLES
    )
    title: str | None = Field(
        description="Название упражнения", max_length=50, default=None, examples=TITLE_EXAMPLES
    )
    preview_image: str | None = Field(
        description="Изображение превью", default=None, examples=IMAGE_EXAMPLES
    )
    background_image: str | None = Field(
        description="Изображение фона", default=None, examples=IMAGE_EXAMPLES
    )
    text_id: UUID | None = Field(
        description="Идентификатор текста", default=None, examples=ID_EXAMPLES
    )
    lang: ExerciseLang | None = Field(
        description="Язык упражнения", default=None, examples=LANG_EXAMPLES
    )
    tags: list[ExerciseTag] | None = Field(
        description="Теги упражнения", default=None, examples=TAGS_EXAMPLES
    )


class UpdateExerciseResponse(BaseSchema):
    """Данные, отправляемые в ответ на запрос изменения информации об упражнении."""

    id: UUID = Field(description="Идентификатор упражнения", examples=ID_EXAMPLES)
    seq_number: int = Field(description="Номер упражнения", gt=0, examples=SEQ_NUMBER_EXAMPLES)
    title: str = Field(description="Название упражнения", max_length=50, examples=TITLE_EXAMPLES)
    difficulty: int = Field(description="Сложность упражнения", ge=0, examples=DIFFICYLTY_EXAMPLES)
    preview_image: str | None = Field(
        description="Изображение превью", default=None, examples=IMAGE_EXAMPLES
    )
    background_image: str | None = Field(
        description="Изображение фона", default=None, examples=IMAGE_EXAMPLES
    )
    text_id: UUID = Field(description="Идентификатор текста", examples=ID_EXAMPLES)
    lang: ExerciseLang = Field(description="Язык упражнения", examples=LANG_EXAMPLES)
    tags: list[ExerciseTag] = Field(
        description="Теги упражнения", default=[], examples=TAGS_EXAMPLES
    )
