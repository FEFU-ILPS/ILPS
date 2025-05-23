from pydantic_settings import BaseSettings, SettingsConfigDict

from .services import ServicesConfiguration
from .graylog import GraylogConfiguration


class ProjectConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GATEWAY_")

    # * Вложенные группы настроек
    services: ServicesConfiguration = ServicesConfiguration()
    graylog: GraylogConfiguration = GraylogConfiguration()

    # * Опциональные переменные
    DEBUG_MODE: bool = False
    SERVICE_NAME: str = "ilps-api-gateway"


configs = ProjectConfiguration()

__all__ = ("configs",)
