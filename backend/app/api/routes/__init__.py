from fastapi import APIRouter

from .fields import router as fields_router
from .health import router as health_router
from .users import router as users_router
from .auth import router as auth_router
from .interests import router as interests_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(fields_router, prefix="/fields", tags=["fields"])
api_router.include_router(interests_router, prefix="/interests", tags=["interests"])

__all__ = ["api_router"]
