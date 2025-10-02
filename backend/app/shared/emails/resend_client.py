# app/shared/emails/resend_mailer.py

import resend

from .email_client import EmailClient
from ..config import settings
from ...exceptions.exceptions import APIError


class ResendMailer(EmailClient):
    def __init__(self):
        # Configure API key if available; otherwise error gracefully on use
        api_key = settings.email_service_token
        if not api_key:
            # Do not leak configuration details to callers
            raise APIError(
                "Email service is not configured.",
                status_code=503,
                title="EmailServiceUnavailable",
            )
        resend.api_key = api_key

    def send(
            self,
            to: list[str],
            subject: str,
            html: str,
            text: str | None = None,
            from_: str | None = None,
    ) -> dict:
        if settings.env != "prod":
            to = settings.default_to_email

        params = {
            "from": from_ or "onboarding@resend.dev",
            "to": to,
            "subject": subject,
            "html": html,
        }
        if text:
            params["text"] = text

        return resend.Emails.send(params)


def get_email_client() -> ResendMailer:
    return ResendMailer()
