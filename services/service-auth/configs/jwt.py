from pydantic_settings import BaseSettings, SettingsConfigDict


class JwtConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_JWT_")

    # ! Обязательные переменные
    SECRET: str

    # * Опциональные переменные
    ALGORITHM: str = "HS512"
    ACCESS_TOKEN_LIFETIME: int = 60
