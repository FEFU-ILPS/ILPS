from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from configs import configs
from database.models import User


async def identificate_user(db: AsyncSession, name: str) -> Optional[User]:
    """Производит идентификацию пользхователя, путем поиска записи
    о нем в базе данных.

    Args:
        db (AsyncSession): Асинхронная сессия подключения к базек данных.
        name (str): Имя пользователя.

    Returns:
        Optional[User]: Обьект пользователя.
    """
    stmt = select(User).where(User.name == name)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def encode_access_token(subject: UUID, expiration_delta: Optional[timedelta] = None) -> str:
    """Генерирует токен доступа для пользователя (subject).

    Args:
        subject (UUID): UUID пользователя.
        expiration_delta (Optional[timedelta]): Дельта времени, через которое токен просрочится.

    Returns:
        str: Токен доступа.
    """
    expiration_delta = expiration_delta or timedelta(minutes=configs.jwt.ACCESS_TOKEN_LIFETIME)
    now_time = datetime.now(tz=timezone.utc)

    payload = {
        "sub": str(subject),
        "iss": configs.SERVICE_NAME,
        "exp": now_time + expiration_delta,
        "iat": now_time,
    }

    return jwt.encode(
        payload=payload,
        key=configs.jwt.SECRET,
        algorithm=configs.jwt.ALGORITHM,
    )


async def decode_access_token(access_token: str) -> Optional[UUID]:
    """Декодирует и валидирует токен доступа пользователя,
    возвращая `UUID` (subject) последнего.
    В случае, если токен не действителен или не валиден, то
    вернется `None`.

    Args:
        access_token (str): JWT Токен доступа.

    Returns:
        Optional[UUID]: UUID пользователя.
    """
    try:
        payload = jwt.decode(
            jwt=access_token,
            key=configs.jwt.SECRET,
            algorithms=[configs.jwt.ALGORITHM],
            issuer=configs.SERVICE_NAME,
            leeway=2,
            options={
                "require": [
                    "exp",
                    "iss",
                    "sub",
                    "iat",
                ]
            },
        )

    except (jwt.MissingRequiredClaimError, jwt.ExpiredSignatureError, jwt.InvalidIssuerError):
        return None

    user_uuid = payload.get("sub")
    return UUID(user_uuid)
