from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import User
from schemas.users import UserResponse

from .utils.pagination import PaginatedResponse, Pagination

router = APIRouter(prefix="/users")


@router.get("/", summary="Получить всех пользователей")
async def get_users(
    pg: Annotated[Pagination, Depends()],
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[UserResponse]:
    """Постранично возвращает список всех зарегистрированных пользователей."""
    stmt = select(User).offset(pg.skip).limit(pg.size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    stmt = select(func.count()).select_from(User)
    result = await db.execute(stmt)
    total = result.scalar_one()

    items = [UserResponse.model_validate(user) for user in users]

    return PaginatedResponse[UserResponse](
        items=items,
        page=pg.page,
        size=pg.size,
        total=total,
    )


@router.get("/{uuid}")
async def get_user(
    uuid: Annotated[UUID, Path(...)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Возвращает информацию о конкретном зарегистрированном пользователе по его UUID."""
    stmt = select(User).where(User.id == uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return UserResponse.model_validate(user)


@router.patch("/{uuid}")
async def update_user(
    uuid: Annotated[UUID, Path(...)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    # TODO: Write me
    pass
