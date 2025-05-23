from typing import Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

M = TypeVar("M", bound=BaseModel)


class Pagination(BaseModel):
    page: int = Field(gt=0, default=1, description="Номер страницы")
    size: int = Field(ge=0, default=50, description="Размер страницы")

    @computed_field
    @property
    def skip(self) -> int:
        """Количество записей на пропуск."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[M]):
    items: list[M] = Field(description="Список объектов")
    page: int = Field(gt=0, description="Номер страницы")
    size: int = Field(ge=0, description="Размер страницы")
    total: int = Field(ge=0, description="Всего объектов")

    @computed_field(description="Всего страниц")
    @property
    def total_pages(self) -> int:
        """Количество страниц всего."""
        return (self.total + self.size - 1) // self.size
