import re
from uuid import UUID

from fastapi import Body
from pydantic import BaseModel, Field, field_validator
from examples import (
    NAME_EXAMPLES,
    PASSWORD_EXAMPLES,
    EMAIL_EXAMPLES,
    ID_EXAMPLES,
    TOKEN_EXAMPLES,
    JWT_EXAMPLES,
)


class AuthenticateUserRequest(BaseModel):
    """Схема аутентифицированного пользователя."""

    username: str = Body(max_length=255, description="Имя пользователя", examples=NAME_EXAMPLES)
    password: str = Body(
        max_length=40, description="Пароль пользователя", min_length=8, examples=PASSWORD_EXAMPLES
    )


class AuthenticateUserResponse(BaseModel):
    """Схема ответа аутентифицированного пользователя."""

    access_token: str = Field(description="JWT токен доступа", examples=JWT_EXAMPLES)
    token_type: str = Field(
        description="Тип токена доступа", default="Bearer", examples=TOKEN_EXAMPLES
    )


class RegisterUserRequest(BaseModel):
    """Схема запроса регистрации пользователя."""

    name: str = Field(description="Имя пользователя", max_length=255, examples=NAME_EXAMPLES)
    email: str = Field(
        description="Электронная почта пользователя", max_length=255, examples=EMAIL_EXAMPLES
    )
    password: str = Field(
        description="Пароль пользователя", max_length=40, min_length=8, examples=PASSWORD_EXAMPLES
    )

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

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        """Валидатор пароля игрока.

        Args:
            value (str): Невалидированное значение.

        Raises:
            ValueError: Неверный формат пароля.

        Returns:
            str: Валидированное значение.
        """
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("Password must contain at least one special character")

        return value


class RegisterUserResponse(BaseModel):
    """Схема ответа регистрации пользователя."""

    id: UUID = Field(description="Идентификатор пользователя", examples=ID_EXAMPLES)
    name: str = Field(description="Имя пользователя", max_length=255, examples=NAME_EXAMPLES)


class AuthorizeUserRequest(BaseModel):
    """Схема запроса авторизации пользователя."""

    access_token: str = Field(description="JWT токен доступа", examples=JWT_EXAMPLES)


class AuthorizeUserResponse(BaseModel):
    """Схема ответа авторизации пользователя."""

    id: UUID = Field(description="Идентификатор пользователя", examples=ID_EXAMPLES)
    name: str = Field(description="Имя пользователя", max_length=255, examples=NAME_EXAMPLES)
    is_admin: bool = Field(description="Флаг админ прав", examples=[True, False])
