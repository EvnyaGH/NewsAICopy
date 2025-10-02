from __future__ import annotations

import secrets

from fastapi import Depends

from app.repositories.session_repository import (
    SessionRepository,
    get_session_repository,
    SessionData,
)


class SessionService:
    """Handles session creation and deletion."""

    def __init__(self, session_repo: SessionRepository) -> None:
        self._repo = session_repo

    async def create_session(
            self, user_id: str, roles: list[str] | None = None
    ) -> tuple[str, int, SessionData]:
        """Creates a new session for a user.

        Args:
            user_id: The ID of the user.
            roles: A list of roles associated with the user.

        Returns:
            A tuple containing the session ID (sid), session TTL in seconds,
            and the created SessionData object.
        """
        return await self._repo.create(user_id, roles or [])

    async def delete_session(self, sid: str) -> None:
        """Deletes a session by its ID.

        Args:
            sid: The session ID to delete.
        """
        await self._repo.delete(sid)


def get_session_service(
        repo: SessionRepository = Depends(get_session_repository),
) -> SessionService:
    return SessionService(session_repo=repo)
