import json

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from configs import configs
from schemas.auth import AuthorizedUser
from service_logging import logger

from .http_proxy import proxy_request

# ! На данный момент это не будет работать непостредственно в Swagger
# ! URL /auth/login принимает JSON, а не URL-Encoded, что подразумевается
# ! в использовании OAuthPasswordBearer.
# TODO: Рассмотреть варианты
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class RouteProtection:
    """Класс, предоставляющий интерфейс зависимости FastAPI для защиты
    роутов от неавторизованного доступа.
    """

    def __init__(self, only_admin: bool = False) -> None:
        """Конструктор класса.

        Args:
            only_admin (bool, optional): Доступ только администраторам. Defaults to False.
        """
        self.only_admin = only_admin

    async def __call__(self, token: str = Depends(oauth2_scheme)) -> AuthorizedUser:
        """Зависимость FastAPI, которая парсит токен доступа из заголовка Authorization.
        Производит авторизацию пользователя, возвращает информацию о нем и его правах в системе.
        """
        logger.info("The authorization process has begun...")
        async with proxy_request(configs.services.auth.URL) as client:
            try:
                response = await client.post("/verify", content=json.dumps({"access_token": token}))
                response.raise_for_status()

            except HTTPException as error:
                logger.info("The authorization process has been interrupted.")

                raise HTTPException(
                    status_code=error.status_code,
                    detail=error.detail,
                    headers={"WWW-Authenticate": "Bearer"},
                )

        subject = AuthorizedUser(**response.json())
        logger.info(f"User {subject.name} authenticated.")
        self.__check_rights(subject)

        return subject

    def __check_rights(self, subject: AuthorizedUser) -> None:
        """Проверка необходимых прав у авторизованного пользователя.

        Args:
            subject (AuthorizedUser): Данные авторизованного пользователя.

        Raises:
            HTTPException: 403. Доступ запрещён из-за нехватки прав.
        """
        if not subject.is_admin and self.only_admin:
            logger.info(f"User{subject.name} does not have access rights to this resource.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action is unavailable",
            )

        logger.info(f"User {subject.name} authorized.")
