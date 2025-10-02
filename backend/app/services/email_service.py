from __future__ import annotations

import secrets
from hashlib import sha256

from fastapi import Depends

from app.shared.config import settings
from app.shared.emails.email_client import EmailClient
from app.shared.emails.resend_client import get_email_client
from app.shared.emails.templates import render_verify_email
from app.repositories.email_repository import get_email_repository, EmailRepository


class EmailService:
    """Handles sending emails and verification."""

    def __init__(self, auth_repo: EmailRepository, mailer: EmailClient) -> None:
        self._repo = auth_repo
        self._mailer = mailer

    async def send_verification_email(self, to_email: str):
        # 1) Make an opaque random token for the user
        raw_token = secrets.token_urlsafe(32)  # send this to the user

        # 2) Store only a hash server-side
        token_hash = sha256(raw_token.encode()).hexdigest()

        verification_link = f"{settings.frontend_url}/verify?token={raw_token}"

        subject = "Verify your email"
        html = render_verify_email(verification_link)
        text = f"Hello,\n\nPlease verify your email by visiting this link: {verification_link}\n\nIf you didn’t create an account, you can ignore this email."

        await self._repo.set(token_hash.__str__(), to_email, 300)

        return self._mailer.send([to_email], subject, html, text=text)

    async def verify_email_token(self, raw_token: str) -> str | None:
        token_hash = sha256(raw_token.encode()).hexdigest()
        return await self._repo.get(token_hash)

    async def remove_email_token(self, raw_token: str) -> str | None:
        token_hash = sha256(raw_token.encode()).hexdigest()
        return await self._repo.delete(token_hash)


def get_email_service(
        repo: EmailRepository = Depends(get_email_repository),
        mailer: EmailClient = Depends(get_email_client),
) -> EmailService:
    return EmailService(auth_repo=repo, mailer=mailer)
