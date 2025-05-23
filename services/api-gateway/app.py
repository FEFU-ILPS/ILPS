import hashlib
from contextlib import asynccontextmanager
from random import randbytes
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from routers import auth_router, exercises_router, health_router, tasks_router, texts_router
from service_logging import logger


@asynccontextmanager
async def lifespan(_: FastAPI):
    # До запуска приложения
    logger.info("FastAPI application starting up...")

    yield

    # После запуска
    logger.info("FastAPI application shutting down...")


gateway = FastAPI(lifespan=lifespan)


@gateway.middleware("http")
async def add_request_hash(request: Request, call_next: Callable):
    request_hash = hashlib.sha1(randbytes(32)).hexdigest()[:10]
    with logger.contextualize(request_hash=request_hash):
        response = await call_next(request)
        return response


gateway.include_router(health_router)
gateway.include_router(auth_router)
gateway.include_router(texts_router)
gateway.include_router(tasks_router)
gateway.include_router(exercises_router)

gateway.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Изменить в проде
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
