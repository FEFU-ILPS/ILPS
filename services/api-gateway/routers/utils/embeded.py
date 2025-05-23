from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

M = TypeVar("M", bound=BaseModel)


class Embedded(BaseModel):
    """Класс Query параметров, необходимых для указания расширения запроса."""

    entities: str = Field(description="Список сущностей для расширения запроса", default="")

    def get_entities(self) -> list[str]:
        """Возвращает распаршеный список сущностей для расширение запроса.

        Returns:
            list[str]: Список сущностей.
        """
        return [entity.strip() for entity in self.entities.split(",")]


class EmbeddedResponse(BaseModel, Generic[M]):
    """Класс ответа с расширением."""

    item: M = Field(description="Целевой объект")
    embedded: dict[str, dict[str, Any]] = Field(description="Расширение запроса", default={})
