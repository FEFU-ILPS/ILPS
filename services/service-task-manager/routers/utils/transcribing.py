from io import BytesIO


from sqlalchemy.ext.asyncio import AsyncSession

from configs import configs
from database.models import Task
from database.types import Status

from .http_proxy import proxy_request
from service_logging import logger


async def transcribe_audio(audio_file: BytesIO, task_obj: Task, db: AsyncSession) -> str:
    """Функция передает поток байтов аудиофайла на сервис транскрибирования,
    параллельно меняя статус задачи.

    Функция при помощи сервиса транскрибирования возвращает строку,
    которая является фонетической записью прочитанного текста.

    Args:
        audio_file (BytesIO): Поток байтов аудиофайала.
        task_obj (Task): Обьект ORM задачи.
        db (AsyncSession): Обьект сессии базы данных.

    Returns:
        str: Фонетическая запись текста.
    """
    task_obj.status = Status.TRANSCRIBING
    await db.commit()

    logger.info("Transcribing audio file....")
    async with proxy_request(configs.services.transcribing.URL) as client:
        response = await client.post(
            "/",
            data={"lang": "english"},
            files={"file": ("audio.wav", audio_file.getvalue(), "audio/wav")},
        )
        response.raise_for_status()

        return response.json()["transcription"]
