from pathlib import Path
from typing import Iterator

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelConfiguration(BaseSettings):
    # ! Обязательные переменные
    LANG: str
    GDRIVE_URL: str

    @field_validator("LANG", mode="before")
    @classmethod
    def capitalize(cls, value: str) -> str:
        """Валидатор, приводящий значение поля LANG в lowercase."""
        return value.lower()


def get_model_configuration(lang_name: str) -> ModelConfiguration:
    env_namespace = f"TRANSCRIBING_MODEL_{lang_name.upper()}_"

    class SpecificModelConfiguration(ModelConfiguration):
        model_config = SettingsConfigDict(env_prefix=env_namespace)

    return SpecificModelConfiguration()


class ModelsConfiguration(BaseSettings):
    __models: list[ModelConfiguration] = []

    # * Вложенные группы настроек
    english: ModelConfiguration = get_model_configuration("english")

    # * Опциональные переменные
    local_path: Path = Path("./models/src")

    def git_dir(self, lang_name: str) -> Path:
        """Функция возвращает обьект пути до директории
        с языковой моделью torch.

        Args:
            lang (str): Название языка.

        Returns:
            Path: Путь к директории с модель.
        """
        return self.local_path / lang_name

    def count(self) -> int:
        """Функция возвращает количество моделей, переданных
        сервису для загрузки.

        Returns:
            int: Количество моделей.
        """
        return len(self.__models)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__models.extend([self.english])

    def __iter__(self) -> Iterator[ModelConfiguration]:
        """Функция возвращает объект итератор, позволяющий
        пробежаться по списку моделей для загрузки в сервис.

        Returns:
            Iterator[ModelConfiguration]: Объект итератора моделей.
        """
        return iter(self.__models)
