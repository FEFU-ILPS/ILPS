from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_DB_")

    # ! Обязательные переменные
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str

    # * Опциональные переменные
    POSTGRES_USER: str = "service_auth"
    POSTGRES_NAME: str = "auth"
    POSTGRES_PORT: int = 5432

    @property
    def URL(self) -> str:
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}".format(
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            db_name=self.POSTGRES_NAME,
        )
