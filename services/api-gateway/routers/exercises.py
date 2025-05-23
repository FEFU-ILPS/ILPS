from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path

from configs import configs
from schemas.exercises import (
    CreateExerciseRequest,
    CreateExerciseResponse,
    DeleteExerciseResponse,
    DetailExerciseResponse,
    ExerciseResponse,
    UpdateExerciseRequest,
    UpdateExerciseResponse,
)
from service_logging import logger

from .utils.embeded import Embedded, EmbeddedResponse
from .utils.http_proxy import proxy_request
from .utils.pagination import PaginatedResponse, Pagination
from .utils.protection import AuthorizedUser, RouteProtection

router = APIRouter(prefix="/exercises")

protected = RouteProtection()
admin_protected = RouteProtection(only_admin=True)


@router.get("/", summary="Получить список всех упражнений", tags=["Exercises"])
async def get_exercises(
    pg: Annotated[Pagination, Depends()],
    _: Annotated[AuthorizedUser, Depends(protected)],
) -> PaginatedResponse[ExerciseResponse]:
    """Постранично возвращает список всех обучающих упражнений."""
    logger.info("Getting the exercise list...")
    async with proxy_request(configs.services.exercises.URL) as client:
        response = await client.get("/", params={"page": pg.page, "size": pg.size})
        response.raise_for_status()

    paginated_items = PaginatedResponse[ExerciseResponse](**response.json())
    logger.success(f"Received {len(paginated_items.items)} exercises.")

    return paginated_items


@router.get("/{uuid}", summary="Получить детальную информацию об упражнении", tags=["Exercises"])
async def get_exercise(
    uuid: Annotated[UUID, Path(...)],
    _: Annotated[AuthorizedUser, Depends(protected)],
) -> DetailExerciseResponse:
    """Возвращает полную информацию о конкретном упражнении по его UUID."""
    logger.info("Getting information about an exercise...")
    async with proxy_request(configs.services.exercises.URL) as client:
        response = await client.get(f"/{uuid}")
        response.raise_for_status()

    item = DetailExerciseResponse(**response.json())
    logger.success(f"Exercise received: ({item.seq_number}){item.id}")

    return item


@router.get(
    "/{uuid}/embedded",
    summary="Получить детальную информацию об упражнении с дополнительными полями",
    tags=["Exercises"],
)
async def get_embedded_exercise(
    uuid: Annotated[UUID, Path(...)],
    emb: Annotated[Embedded, Depends()],
    _: Annotated[AuthorizedUser, Depends(protected)],
) -> EmbeddedResponse[DetailExerciseResponse]:
    """Возвращает полную информацию с доплнительными полями о конкретном упражнении по его UUID."""

    embed = {}
    entities = emb.get_entities()

    logger.info("Getting embedded information about an exercise...")
    async with proxy_request(configs.services.exercises.URL) as client:
        response = await client.get(f"/{uuid}")
        response.raise_for_status()
        item = DetailExerciseResponse(**response.json())

    if "text" in entities:
        logger.info("Getting embedding text information...")
        async with proxy_request(configs.services.texts.URL) as client:
            response = await client.get(f"/{item.text_id}")
            response.raise_for_status()
            embed["text"] = response.json()

    embedded_item = EmbeddedResponse[DetailExerciseResponse](item=item, embedded=embed)
    logger.success(f"Exercise received: ({embedded_item.item.seq_number}){embedded_item.item.id}")

    return embedded_item


@router.post("/", summary="Добавить упражнение в систему", tags=["Exercises"])
async def create_exercise(
    data: Annotated[CreateExerciseRequest, Body(...)],
    _: Annotated[AuthorizedUser, Depends(admin_protected)],
) -> CreateExerciseResponse:
    """Добавляет новое упражнение в систему."""
    logger.info("Creating an exercise...")
    async with proxy_request(configs.services.exercises.URL) as client:
        response = await client.post("/", content=data.model_dump_json(exclude_none=True))
        response.raise_for_status()

    item = CreateExerciseResponse(**response.json())
    logger.success(f"Exercise has been created: ({item.seq_number}){item.id}")

    return item


@router.delete("/{uuid}", summary="Удалить упражнение из системы", tags=["Exercises"])
async def delete_exercise(
    uuid: Annotated[UUID, Path(...)],
    _: Annotated[AuthorizedUser, Depends(admin_protected)],
) -> DeleteExerciseResponse:
    """Удаляет упражнение из системы по его UUID."""
    logger.info("Deleting an exercise...")
    async with proxy_request(configs.services.exercises.URL) as client:
        response = await client.delete(f"/{uuid}")
        response.raise_for_status()

    item = DeleteExerciseResponse(**response.json())
    logger.success(f"Exercise has been deleted: ({item.seq_number}){item.id}")

    return item


@router.patch("/{uuid}", summary="Обновить данные о тексте", tags=["Exercises"])
async def update_exercise(
    uuid: Annotated[UUID, Path(...)],
    data: Annotated[UpdateExerciseRequest, Body(...)],
    _: Annotated[AuthorizedUser, Depends(admin_protected)],
) -> UpdateExerciseResponse:
    """Обновляет данные текста по его UUID."""
    logger.info("Updating an exercise...")
    async with proxy_request(configs.services.exercises.URL) as client:
        response = await client.patch(f"/{uuid}", content=data.model_dump_json(exclude_none=True))
        response.raise_for_status()

    item = UpdateExerciseResponse(**response.json())
    logger.success(f"Exercise has been updated: ({item.seq_number}){item.id}")

    return item
