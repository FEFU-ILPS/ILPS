from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import LearningText
from schemas import (
    CreateLearningTextRequest,
    CreateLearningTextResponse,
    DeleteLearningTextResponse,
    DetailLearningTextResponse,
    LearningTextResponse,
    UpdateLearningTextRequest,
    UpdateLearningTextResponse,
)

from .utils.pagination import PaginatedResponse, Pagination

router = APIRouter()


@router.get("/", summary="Получить список всех текстов")
async def get_texts(
    pg: Annotated[Pagination, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PaginatedResponse[LearningTextResponse]:
    """Постранично возвращает список всех обучающих текстов."""
    stmt = select(LearningText).offset(pg.skip).limit(pg.size)
    result = await db.execute(stmt)
    texts = result.scalars().all()

    stmt = select(func.count()).select_from(LearningText)
    result = await db.execute(stmt)
    total = result.scalar_one()

    items = [LearningTextResponse.model_validate(text) for text in texts]

    return PaginatedResponse[LearningTextResponse](
        items=items,
        page=pg.page,
        size=pg.size,
        total=total,
    )


@router.get("/{uuid}", summary="Получить детальную информацию о тексте")
async def get_text(
    uuid: Annotated[UUID, Path(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DetailLearningTextResponse:
    """Возвращает полную информацию о конкретном тексте по его UUID."""
    stmt = select(LearningText).where(LearningText.id == uuid)
    result = await db.execute(stmt)
    text = result.scalar_one_or_none()

    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Text not found.",
        )

    return DetailLearningTextResponse.model_validate(text)


@router.post("/", summary="Добавить текст в систему")
async def create_text(
    data: Annotated[CreateLearningTextRequest, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CreateLearningTextResponse:
    """Добавляет новый текст в систему."""

    try:
        text = LearningText(
            title=data.title,
            value=data.value,
            transcription=data.transcription,
        )
        db.add(text)
        await db.commit()
        await db.refresh(text)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text with this data already exists.",
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error ocured while creating text.",
        )

    return CreateLearningTextResponse.model_validate(text)


@router.delete("/{uuid}", summary="Удалить текст из системы")
async def delete_text(
    uuid: Annotated[UUID, Path(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeleteLearningTextResponse:
    """Удаляет текст из системы по его UUID."""
    stmt = select(LearningText).where(LearningText.id == uuid)
    result = await db.execute(stmt)
    text = result.scalar_one_or_none()

    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Text not found.",
        )

    await db.delete(text)
    await db.commit()

    return DeleteLearningTextResponse.model_validate(text)


@router.patch("/{uuid}", summary="Обновить данные о тексте")
async def update_text(
    uuid: Annotated[UUID, Path(...)],
    data: Annotated[UpdateLearningTextRequest, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UpdateLearningTextResponse:
    """Обновляет данные текста по его UUID."""
    stmt = select(LearningText).where(LearningText.id == uuid)
    result = await db.execute(stmt)
    text = result.scalar_one_or_none()

    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Text not found.",
        )

    try:
        data = data.model_dump(exclude_none=True)
        for field in data:
            setattr(text, field, data[field])

        db.add(text)
        await db.commit()
        await db.refresh(text)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text with this data already exists.",
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error ocured while updating text.",
        )

    return UpdateLearningTextResponse.model_validate(text)
