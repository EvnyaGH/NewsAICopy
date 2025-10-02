from __future__ import annotations


class APIError(Exception):
    """Base application error with HTTP status and title."""

    status_code: int = 400
    title: str = "Bad Request"

    def __init__(self, message: str | None = None, *, status_code: int | None = None, title: str | None = None) -> None:
        super().__init__(message or self.title)
        if status_code is not None:
            self.status_code = status_code
        if title is not None:
            self.title = title


class AuthenticationError(APIError):
    status_code = 401
    title = "AuthenticationError"


class InvalidCredentialsError(AuthenticationError):
    title = "InvalidCredentialsError"

class UserDoesNotExist(APIError):
    status_code = 401
    title = "UserDoesNotExist"

class InvalidTokenError(AuthenticationError):
    title = "InvalidTokenError"


class TokenRevokedError(AuthenticationError):
    title = "TokenRevokedError"


class MissingRefreshTokenError(AuthenticationError):
    title = "MissingRefreshTokenError"


class InvalidRefreshTokenError(AuthenticationError):
    title = "InvalidRefreshTokenError"

class EmailVerificationError(APIError):
    title = "EmailVerificationError"

class EmailVerificationNotVerified(APIError):
    status_code = 401
    title = "EmailVerificationNotVerified"

class DuplicateInterestError(APIError):
    status_code = 409
    title = "DuplicateInterestError"
