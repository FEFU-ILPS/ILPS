from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseConfiguration


class ProjectConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TEXTS_")

    # * Вложенные группы настроек
    database: DatabaseConfiguration = DatabaseConfiguration()

    # * Опциональные переменные
    DEBUG_MODE: bool = True
    SERVICE_NAME: str = "ilps-service-texts"


configs = ProjectConfiguration()

__all__ = ("configs",)
