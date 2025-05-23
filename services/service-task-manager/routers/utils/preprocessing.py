from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession

from configs import configs
from database.models import Task
from database.types import Status
from service_logging import logger

from .http_proxy import proxy_request


async def preprocess_audio(audio_file: BytesIO, task_obj: Task, db: AsyncSession) -> BytesIO:
    """Функция передает поток байтов аудиофайла на сервис предобработки,
    параллельно меняя статус задачи.

    Функция при помощи сервиса предобработки возвращает поток байтов
    аудиофайла с изменеными значениями и свойств аудио: Частота дискретизации, усиление и т.п.

    Args:
        audio_file (BytesIO): Поток байтов аудиофайала.
        task_obj (Task): Обьект ORM задачи.
        db (AsyncSession): Обьект сессии базы данных.

    Returns:
        BytesIO: Поток байтов обработанного аудиофайла.
    """
    task_obj.status = Status.PREPROCESSING
    await db.commit()

    logger.info("Preprocessing audio file....")
    async with proxy_request(configs.services.preprocessing.URL) as client:
        response = await client.post(
            "/", files={"file": ("audio.pcm", audio_file.getvalue(), "application/octet-stream")}
        )
        response.raise_for_status()

        return BytesIO(response.content)
