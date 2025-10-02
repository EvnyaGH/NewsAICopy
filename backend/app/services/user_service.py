from __future__ import annotations

from datetime import datetime

from fastapi import Depends

from app.exceptions.exceptions import EmailVerificationError
from app.models.user import User
from app.repositories.user_repository import UserRepository, get_user_repository
from app.services.email_service import EmailService, get_email_service


class UserService:
    def __init__(self, repo: UserRepository, email_service: EmailService) -> None:
        self._repo = repo
        self._email_service = email_service

    def find_by_id(self, user_id) -> User | None:
        return self._repo.get_by_id(user_id)

    def find_by_email(self, email) -> User | None:
        return self._repo.get_by_email(email)

    def get_roles(self, user_id) -> list[str]:
        return self._repo.get_role_names(user_id)

    async def register(self, user: User, roles: list[str]) -> None:
        self._repo.insert_user(user, roles)
        await self._email_service.send_verification_email(to_email=user.email)
        return

    async def verify_email(self, token: str) -> None:
        email = await self._email_service.verify_email_token(token)

        if not email:
            raise EmailVerificationError("Invalid email verification token")

        self._repo.update_user_by_email(email, {'email_verified_at': datetime.now()})
        await self._email_service.remove_email_token(token)

        return

    async def send_verification_email(self, email: str) -> None:
        await self._email_service.send_verification_email(to_email=email)
        return


def get_user_service(repo: UserRepository = Depends(get_user_repository),
                     email_service: EmailService = Depends(get_email_service)) -> UserService:
    return UserService(repo, email_service)
