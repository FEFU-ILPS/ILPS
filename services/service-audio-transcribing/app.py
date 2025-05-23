import hashlib
from contextlib import asynccontextmanager
from random import randbytes
from typing import Callable

from fastapi import FastAPI, Request

from configs import configs
from models import model_manager
from routers import health_router, transcribing_router
from service_logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_startup
    await model_manager.load_models(
        rm_files=not configs.DEBUG_MODE,
    )

    yield

    # on_shutdown


service = FastAPI(lifespan=lifespan)


@service.middleware("http")
async def add_request_hash(request: Request, call_next: Callable):
    request_hash = hashlib.sha1(randbytes(32)).hexdigest()[:10]
    with logger.contextualize(request_hash=request_hash):
        response = await call_next(request)
        return response


service.include_router(transcribing_router)
service.include_router(health_router)
