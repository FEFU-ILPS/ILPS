from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import Exercise
from schemas import (
    CreateExerciseRequest,
    CreateExerciseResponse,
    DeleteExerciseResponse,
    DetailExerciseResponse,
    ExerciseResponse,
    UpdateExerciseRequest,
    UpdateExerciseResponse,
)

from .utils.pagination import PaginatedResponse, Pagination

router = APIRouter()


@router.get("/", summary="Получить список всех упражнений")
async def get_exercises(
    pg: Annotated[Pagination, Depends()],
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ExerciseResponse]:
    """Постранично возвращает список всех обучающих упражнений."""
    stmt = select(Exercise).offset(pg.skip).limit(pg.size)
    result = await db.execute(stmt)
    exercises = result.scalars().all()

    stmt = select(func.count()).select_from(Exercise)
    result = await db.execute(stmt)
    total = result.scalar_one()

    items = [ExerciseResponse.model_validate(exercise) for exercise in exercises]

    return PaginatedResponse[ExerciseResponse](
        items=items,
        page=pg.page,
        size=pg.size,
        total=total,
    )


@router.get("/{uuid}", summary="Получить детальную информацию об упражнении")
async def get_exercise(
    uuid: Annotated[UUID, Path(...)],
    db: AsyncSession = Depends(get_db),
) -> DetailExerciseResponse:
    """Возвращает полную информацию о конкретном упражнении по его UUID."""
    stmt = select(Exercise).where(Exercise.id == uuid)
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()

    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found.",
        )

    return DetailExerciseResponse.model_validate(exercise)


@router.post("/", summary="Добавить упражнение в систему")
async def create_text(
    data: Annotated[CreateExerciseRequest, Body(...)],
    db: AsyncSession = Depends(get_db),
) -> CreateExerciseResponse:
    """Добавляет новое упражнение в систему."""

    try:
        exercise = Exercise(
            title=data.title,
            difficulty=data.difficulty,
            tags=data.tags,
            text_id=data.text_id,
        )
        db.add(exercise)
        await db.commit()
        await db.refresh(exercise)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exercise with this data already exists.",
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error ocured while creating exercise.",
        )

    return CreateExerciseResponse.model_validate(exercise)


@router.delete("/{uuid}", summary="Удалить упражнение из системы")
async def delete_text(
    uuid: Annotated[UUID, Path(...)],
    db: AsyncSession = Depends(get_db),
) -> DeleteExerciseResponse:
    """Удаляет упражнение из системы по его UUID."""
    stmt = select(Exercise).where(Exercise.id == uuid)
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()

    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found.",
        )

    await db.delete(exercise)
    await db.commit()

    return DeleteExerciseResponse.model_validate(exercise)


@router.patch("/{uuid}", summary="Обновить данные об упражнении")
async def update_text(
    uuid: Annotated[UUID, Path(...)],
    data: Annotated[UpdateExerciseRequest, Body(...)],
    db: AsyncSession = Depends(get_db),
) -> UpdateExerciseResponse:
    """Обновляет данные упражнения по его UUID."""
    stmt = select(Exercise).where(Exercise.id == uuid)
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()

    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found.",
        )

    try:
        data = data.model_dump(exclude_none=True)
        for field in data:
            setattr(exercise, field, data[field])

        db.add(exercise)
        await db.commit()
        await db.refresh(exercise)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exercise with this data already exists.",
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error ocured while updating exercise.",
        )

    return UpdateExerciseResponse.model_validate(exercise)
