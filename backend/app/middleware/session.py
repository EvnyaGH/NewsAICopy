from __future__ import annotations

from typing import Callable, Awaitable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

from app.shared.config import settings
from app.repositories.session_repository import SessionRepository
from app.shared.cache import get_redis


class SessionMiddleware(BaseHTTPMiddleware):
    """Loads session from opaque `sid` cookie and attaches to request.state.

    - request.state.session: SessionData | None
    - request.state.user_id: str | None
    - request.state.roles: list[str]
    """

    def __init__(self, app: ASGIApp, repo_provider: Callable[[], SessionRepository] | None = None) -> None:
        super().__init__(app)
        # repo_provider is primarily for testing; in app we will resolve per-request
        self._repo_provider = repo_provider

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable]):
        request.state.session = None
        request.state.user_id = None
        request.state.roles = []

        sid = request.cookies.get(settings.session_cookie_name)
        if sid:
            # Resolve repository from DI on demand
            repo: SessionRepository
            if self._repo_provider:
                repo = self._repo_provider()
            else:
                # Construct repo using Redis from request.app.state
                redis = get_redis(request)
                repo = SessionRepository(redis)
            try:
                data = await repo.get(sid)
                if data:
                    request.state.session = data
                    request.state.user_id = data.user_id
                    request.state.roles = data.roles
            except Exception:
                # On any retrieval error, continue without session
                pass
        response = await call_next(request)
        return response
