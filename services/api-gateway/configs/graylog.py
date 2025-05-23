from pydantic_settings import BaseSettings, SettingsConfigDict


class GraylogConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GATEWAY_GRAYLOG_")

    # * Опциональные переменные
    HOST: str = "localhost"
    PORT: int = 12201
    ENABLE: bool = False
