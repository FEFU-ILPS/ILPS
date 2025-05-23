from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_DEFAULT_")

    # * Опциональные переменные
    ADMIN_NAME: str = "admin"
    ADMIN_EMAIL: str = "admin@ilpsadmin.com"
    ADMIN_PASSWORD: str = "password123"
