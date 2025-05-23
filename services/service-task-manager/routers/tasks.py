from io import BytesIO
from typing import Annotated, List
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Request,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from database import get_db
from database.models import Task
from schemas.tasks import (
    CreateTaskResponse,
    DetailTaskRequest,
    DetailTaskResponse,
    TasksRequest,
    TasksResponse,
)
from service_logging import logger

from .utils.tasks import start_task, stream_task

router = APIRouter()


@router.post("/transcribe", summary="Создать задачу на обработку аудио файла")
async def create_task(
    file: Annotated[UploadFile, File(...)],
    title: Annotated[str, Form(...)],
    user_id: Annotated[UUID, Form(...)],
    text_id: Annotated[UUID, Form(...)],
    background: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CreateTaskResponse:
    """Создаёт задачу на предобработку и транскрибирование аудиофайла.
    Возвращает UUID созданой задачи с ответом 200, выполняя её в фоне.
    """
    logger.info("Creating a pronunciation assessment task...")
    created_task = Task(
        title=title,
        user_id=user_id,
        text_id=text_id,
    )

    db.add(created_task)
    await db.commit()
    await db.refresh(created_task)

    bytestream = BytesIO(await file.read())
    background.add_task(start_task, bytestream, created_task, db)

    item = CreateTaskResponse.model_validate(created_task)
    logger.success(f"Task has been created: {item.id}")

    return item


# * GET был заменен на POST ради Body
@router.post("/", summary="Получить список задач")
async def get_tasks(
    data: Annotated[TasksRequest, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> List[TasksResponse]:
    """Получает список всех задач, когда либо созданных в системе ILPS."""

    logger.info("Getting the task list...")
    stmt = select(Task).where(Task.user_id == data.user_id)
    tasks = await db.execute(stmt)
    tasks = tasks.scalars().all()

    items = [TasksResponse.model_validate(task) for task in tasks]
    logger.success(f"Received {len(items)} tasks.")

    return items


# * GET был заменен на POST ради Body
@router.post("/{uuid}", summary="Получить актуальную информацию о задаче")
async def get_task(
    uuid: Annotated[UUID, Path(...)],
    data: Annotated[DetailTaskRequest, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DetailTaskResponse:
    """Получает текущую информацию по UUID указаной задачи.
    Возвращает полную информацию о задача.
    """

    logger.info("Getting information about a task...")
    stmt = select(Task).where((Task.id == uuid) & (Task.user_id == data.user_id))
    task = await db.execute(stmt)
    task = task.scalar_one_or_none()

    if not task:
        detail = "Task not found."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

    item = DetailTaskResponse.model_validate(task)
    logger.success(f"Task found: {item.id}")

    return item


@router.post("/{uuid}/stream", summary="Получать обновления статуса задачи потоком")
async def monitor_task(
    request: Request,
    uuid: Annotated[UUID, Path(...)],
    data: Annotated[DetailTaskRequest, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EventSourceResponse:
    """Получает информацию об обновлениях статуса задачи
    в реальном времени, используя протокол SSE стриминга.
    """

    logger.info("Getting information about a task...")
    stmt = select(Task).where((Task.id == uuid) & (Task.user_id == data.user_id))
    task = await db.execute(stmt)
    task = task.scalar_one_or_none()

    if not task:
        detail = "Task not found."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

    logger.info("Streaming task status updates....")
    event_generator = stream_task(task, db, request)
    return EventSourceResponse(event_generator)
