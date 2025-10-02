from __future__ import annotations

import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select, update
from fastapi import Depends

from app.models.user import User
from app.models.role import Role, UserRole
from app.api.deps import get_db


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).one_or_none()

    def get_role_names(self, user_id: uuid.UUID) -> list[str]:
        """Return role names assigned to the given user."""
        rows = self.db.execute(
            select(Role.name)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        ).all()
        return [r[0] for r in rows]

    import logging

    def insert_user(self, user: User, roles: list[str]) -> None:
        """Create a new user and assign roles."""
        self.db.add(user)
        self.db.flush()  # Flush to get the user.id

        for role_name in roles:
            role = self.db.query(Role).filter(Role.name == role_name).one_or_none()
            if role:
                user_role = UserRole(user_id=user.id, role_id=role.id)
                self.db.add(user_role)
            else:
                logging.warning(f"Role '{role_name}' not found, skipping.")

    def update_user(self, user_id: uuid.UUID, user: dict) -> int | None:
        """Update a user."""
        self.db.query(User).filter(User.id == user_id).update(user)
        return

    def update_user_by_email(self, email: str, user: dict) -> int | None:
        """Update a user."""
        self.db.execute(
            update(User)
            .where(User.email == email)
            .values(user)
        )
        return

    def commit(self) -> None:
        """Commit changes to database."""
        self.db.commit()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)
