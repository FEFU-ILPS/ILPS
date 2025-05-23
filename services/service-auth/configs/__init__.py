from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseConfiguration
from .default import DefaultConfiguration
from .jwt import JwtConfiguration


class ProjectConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_")

    # * Вложенные группы настроек
    database: DatabaseConfiguration = DatabaseConfiguration()
    jwt: JwtConfiguration = JwtConfiguration()
    default: DefaultConfiguration = DefaultConfiguration()

    # * Опциональные переменные
    DEBUG_MODE: bool = True
    SERVICE_NAME: str = "ilps-service-auth"


configs = ProjectConfiguration()

__all__ = ("configs",)
