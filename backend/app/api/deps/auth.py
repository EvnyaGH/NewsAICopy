from __future__ import annotations

import uuid

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.exceptions.exceptions import AuthenticationError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from .db import get_db


async def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    """Get the current user from the session attached to the request state.

    Raises:
        AuthenticationError: If no user is found in the session.
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise AuthenticationError("Not authenticated")

    try:
        user_pk = uuid.UUID(user_id)
    except (ValueError, TypeError):
        # This should not happen with valid session data but is a safeguard.
        raise AuthenticationError("Invalid user identifier in session")

    user = UserRepository(db).get_by_id(user_pk)
    if not user:
        # This could happen if the user was deleted after the session was created.
        raise AuthenticationError("User not found")

    # Attach roles to the user model if needed by downstream dependencies,
    # though it's often better to use a separate dependency for roles.
    # user.roles = getattr(request.state, "roles", [])

    return user