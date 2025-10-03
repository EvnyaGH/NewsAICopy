from fastapi import APIRouter

from .health import router as health_router
from .users import router as users_router
from .auth import router as auth_router


api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

__all__ = ["api_router"]
