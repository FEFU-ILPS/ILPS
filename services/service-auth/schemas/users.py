import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserResponse(BaseModel):
    """Схема валидации зарегистрированного пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Идентификатор пользователя")
    name: str = Field(max_length=255, description="Имя пользователя")
    email: str = Field(max_length=255, description="Электронная почта пользователя")
    # TODO: Добавить поля, необходимые для OAuth2.0

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        """Валидатор электронной почты пользователя.

        Args:
            value (str): Невалидированное значение.

        Raises:
            ValueError: Неверный формат почты.

        Returns:
            str: Валидированное значение.
        """
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")

        return value
