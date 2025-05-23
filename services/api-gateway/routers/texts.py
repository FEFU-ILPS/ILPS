from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path

from configs import configs
from schemas.texts import (
    CreateLearningTextRequest,
    CreateLearningTextResponse,
    DeleteLearningTextResponse,
    DetailLearningTextResponse,
    LearningTextResponse,
    UpdateLearningTextRequest,
    UpdateLearningTextResponse,
)
from service_logging import logger

from .utils.http_proxy import proxy_request
from .utils.pagination import PaginatedResponse, Pagination
from .utils.protection import AuthorizedUser, RouteProtection

router = APIRouter(prefix="/texts")

protected = RouteProtection()
admin_protected = RouteProtection(only_admin=True)


@router.get("/", summary="Получить список всех текстов", tags=["Texts"])
async def get_texts(
    pg: Annotated[Pagination, Depends()],
    _: Annotated[AuthorizedUser, Depends(protected)],
) -> PaginatedResponse[LearningTextResponse]:
    """Возвращает полный список всех обучающих текстов с краткой информацией."""
    logger.info("Getting the text list...")
    async with proxy_request(configs.services.texts.URL) as client:
        response = await client.get("/", params={"page": pg.page, "size": pg.size})
        response.raise_for_status()

    paginated_items = PaginatedResponse[LearningTextResponse](**response.json())
    logger.success(f"Received {len(paginated_items.items)} texts.")

    return paginated_items


@router.get("/{uuid}", summary="Получить детальную информацию о тексте", tags=["Texts"])
async def get_text(
    uuid: Annotated[UUID, Path(...)],
    _: Annotated[AuthorizedUser, Depends(protected)],
) -> DetailLearningTextResponse:
    """Возвращает полную информацию о конкретном тексте по его UUID."""
    logger.info("Getting information about a text...")
    async with proxy_request(configs.services.texts.URL) as client:
        response = await client.get(f"/{uuid}")
        response.raise_for_status()

    item = DetailLearningTextResponse(**response.json())
    logger.success(f"Text received: {item.id}")

    return item


@router.post("/", summary="Добавить текст в систему", tags=["Texts"])
async def create_text(
    data: Annotated[CreateLearningTextRequest, Body(...)],
    _: Annotated[AuthorizedUser, Depends(admin_protected)],
) -> CreateLearningTextResponse:
    """Добавляет новый текст в систему."""
    logger.info("Creating a text...")
    async with proxy_request(configs.services.texts.URL) as client:
        response = await client.post("/", content=data.model_dump_json(exclude_none=True))
        response.raise_for_status()

    item = CreateLearningTextResponse(**response.json())
    logger.success(f"Text has been created: {item.id}")

    return item


@router.delete("/{uuid}", summary="Удалить текст из системы", tags=["Texts"])
async def delete_text(
    uuid: Annotated[UUID, Path(...)],
    _: Annotated[AuthorizedUser, Depends(admin_protected)],
) -> DeleteLearningTextResponse:
    """Удаляет текст из системы по его UUID."""
    logger.info("Deleting a text...")
    async with proxy_request(configs.services.texts.URL) as client:
        response = await client.delete(f"/{uuid}")
        response.raise_for_status()

    item = DeleteLearningTextResponse(**response.json())
    logger.success(f"Text has been deleted: {item.id}")

    return item


@router.patch("/{uuid}", summary="Обновить данные о тексте", tags=["Texts"])
async def update_text(
    uuid: Annotated[UUID, Path(...)],
    data: Annotated[UpdateLearningTextRequest, Body(...)],
    _: Annotated[AuthorizedUser, Depends(admin_protected)],
) -> UpdateLearningTextResponse:
    """Обновляет данные текста по его UUID."""
    logger.info("Updating a text...")
    async with proxy_request(configs.services.texts.URL) as client:
        response = await client.patch(f"/{uuid}", content=data.model_dump_json(exclude_none=True))
        response.raise_for_status()

    item = UpdateLearningTextResponse(**response.json())
    logger.success(f"Text has been updated: {item.id}")

    return item
