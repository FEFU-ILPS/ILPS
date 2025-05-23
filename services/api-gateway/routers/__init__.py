from .auth import router as auth_router
from .exercises import router as exercises_router
from .health import router as health_router
from .tasks import router as tasks_router
from .texts import router as texts_router

__all__ = (
    "health_router",
    "auth_router",
    "texts_router",
    "tasks_router",
    "exercises_router",
)
