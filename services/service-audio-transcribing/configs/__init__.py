from pydantic_settings import BaseSettings, SettingsConfigDict

from .models import ModelsConfiguration


class ProjectConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TRANSCRIBING_")

    # * Вложенные группы настроек
    models: ModelsConfiguration = ModelsConfiguration()

    # * Опциональные переменные
    DEBUG_MODE: bool = True
    SERVICE_NAME: str = "ilps-service-audio-transcribing"


configs = ProjectConfiguration()

__all__ = ("configs",)
