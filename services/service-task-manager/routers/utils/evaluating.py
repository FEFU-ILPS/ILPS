from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from configs import configs
from database.models import Task
from database.types import Status
from service_logging import logger

from .http_proxy import proxy_request


async def evaluate_transcription(
    transcription: str, task_obj: Task, db: AsyncSession
) -> dict[str, Any]:
    """Функция передает результирующую транскрипцию речи из аудиофайла на сервис отчетов,
    параллельно меняя статус задачи.

    Args:
        transcription (str): Транскрипция, извлеченная из текста.
        task_obj (Task): Обьект ORM задачи.
        db (AsyncSession): Обьект сессии базы данных.

    Returns:
        dict[str, Any]: Отчет по произношению.
    """
    task_obj.status = Status.EVALUATING
    await db.commit()

    logger.info("Evaluating tanscription....")
    async with proxy_request(configs.services.feedback.URL) as client:
        response = await client.post(
            "/", json={"text_id": str(task_obj.text_id), "actual_result": transcription}
        )
        response.raise_for_status()

        return response.json()
