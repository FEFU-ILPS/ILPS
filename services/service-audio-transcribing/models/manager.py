from shutil import rmtree
from typing import Any

import gdown
from gdown.exceptions import FolderContentsMaximumLimitError
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

from configs import configs
from service_logging import logger


class SingletonMeta(type):
    """Метакласс для реализации паттерна синглтон."""

    _instances: dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ModelManager(metaclass=SingletonMeta):
    """Класс для управления загрузкой и хранением моделей и процессоров."""

    def __init__(self) -> None:
        """Инициализирует менеджер моделей."""
        self._models: dict[str, tuple[Any, Any]] = {}

    def get_model(self, model_lang: str) -> tuple[Any, Any]:
        """Возвращает загруженную модель и процессор по имени языка.

        Args:
            model_lang (str): Язык модели.

        Returns:
            Tuple[Any, Any]: Пара (processor, model).

        Raises:
            ValueError: Модель для указанного языка не найдена.
        """
        if not self.is_model_loaded(model_lang):
            raise ValueError(f"Model for the language '{model_lang}' has not been loaded.")

        return self._models[model_lang]

    def list_languages(self) -> list:
        """Возвращает список загруженных языков.

        Returns:
            list: Список языков, для которых загружены модели.
        """
        return list(self._models.keys())

    async def load_models(self, rm_files: bool = True) -> None:
        """Загружает модели с Google Drive и предзагружает их в менеджер.
        Данные для загрузки определяются в конфигурации.

        Raises:
            RuntimeError: Ошибка при загрузке файлов модели с google drive.
        """
        logger.info("Collecting language models...")

        configs.models.local_path.mkdir(parents=True, exist_ok=True)

        loaded = 0
        for model_cfg in configs.models:
            model_lang = model_cfg.LANG
            model_path = configs.models.git_dir(model_lang)

            logger.info(f"Downloading model: {model_lang}")

            if model_path.exists():
                logger.info(f"Model files for '{model_lang}' already downloaded.")

            else:
                try:
                    model_path.mkdir(parents=True, exist_ok=True)
                    downloaded = gdown.download_folder(
                        model_cfg.GDRIVE_URL, output=str(model_path), quiet=True
                    )

                    if downloaded is None:
                        msg = (
                            "The directory is probably empty or an incorrect URL was passed. "
                            "Check the environment variables."
                        )

                        if not list(model_path.iterdir()):
                            model_path.rmdir()

                        raise ValueError(msg)

                    else:
                        logger.info(f"Locally saved at '{model_path}'.")

                except (FolderContentsMaximumLimitError, ValueError) as e:
                    logger.error(f"Unable to download model '{model_lang}': {e}")
                    continue

            if await self._load_model(model_lang, str(model_path), rm_files):
                loaded += 1
                logger.info("Done.")

        if loaded == configs.models.count():
            logger.info("All models loaded successfully.")

        elif not loaded:
            logger.warning(
                "Not a single model has been uploaded. "
                "It is possible that the service remains running, but is inoperable."
            )

        else:
            logger.info(f"Successfully loaded {loaded} of {configs.models.count()} models.")

    async def _load_model(self, model_lang: str, model_path: str, rm_files: bool) -> bool:
        """Загружает модель и процессор по указанному пути.
        Если модель уже загружена, повторная загрузка не выполняется.

        Args:
            language (str): Язык модели.
            model_path (str): Путь до директории с моделью.
        """
        if self.is_model_loaded(model_lang):
            logger.info(
                f"Model and processor for the language '{model_lang}' have already been loaded."
            )

        else:
            try:
                logger.info(f"Loading processor and model for '{model_lang}'...")

                processor = Wav2Vec2Processor.from_pretrained(model_path)
                model = Wav2Vec2ForCTC.from_pretrained(model_path)

                self._models[model_lang] = (processor, model)

                if rm_files:
                    rmtree(model_path, ignore_errors=True)

                logger.info(f"Model for '{model_lang}' loaded succesfully.")

            except Exception as e:
                logger.error(f"Error loading the model for the language '{model_lang}': {str(e)}")
                return False

        return True

    def is_model_loaded(self, model_lang: str) -> bool:
        """Выполяет проверку, была ли загружена модель в менеджер ранее.

        Args:
            model_lang (str): Язык модели.

        Returns:
            bool: Флаг состояния загруженности.
        """
        return model_lang in self._models
