import bcrypt as bc
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from configs import configs

from .engine import LocalAsyncSession
from .models import Password, User


async def init_default_admin() -> None:
    """Функция-скрипт создания стандартного администратора системы на основе переданных данных
    через переменные среды.
    """
    async with LocalAsyncSession() as session:
        try:
            default_admin = User(
                name=configs.default.ADMIN_NAME,
                email=configs.default.ADMIN_EMAIL,
                is_admin=True,
            )
            session.add(default_admin)
            await session.flush()
            await session.refresh(default_admin)

            hash = bc.hashpw(configs.default.ADMIN_PASSWORD.encode(), bc.gensalt())
            default_admin_password = Password(
                user_id=default_admin.id,
                hash=hash.decode(),
            )

            session.add(default_admin_password)
            await session.commit()
            logger.info("Admin account created.")

        except SQLAlchemyError as _:
            await session.rollback()
            logger.warning("Admin account already exists.")
