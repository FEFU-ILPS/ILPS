from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseConfiguration
from .services import ServicesConfiguration


class ProjectConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MANAGER_")

    # * Вложенные группы настроек
    database: DatabaseConfiguration = DatabaseConfiguration()
    services: ServicesConfiguration = ServicesConfiguration()

    # * Опциональные переменные
    DEBUG_MODE: bool = True
    SERVICE_NAME: str = "ilps-service-task-manager"


configs = ProjectConfiguration()

__all__ = ("configs",)
