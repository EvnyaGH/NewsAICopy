from __future__ import annotations

import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.exceptions import APIError
from app.schemas.common import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    """Register uniform JSON exception handlers on the FastAPI app.

    Success responses are handled in routes; these handlers ensure all errors
    conform to the envelope: { code, title, message }.
    """

    @app.exception_handler(APIError)
    async def handle_api_error(_, exc: APIError):  # type: ignore[override]
        # Using the exception class name as the title for custom errors
        title = exc.__class__.__name__
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.status_code, title=title, message=str(exc)
            ).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_, exc: StarletteHTTPException):  # type: ignore[override]
        title = "HTTP Error"
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.status_code, title=title, message=str(exc.detail)
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_, exc: RequestValidationError):  # type: ignore[override]
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code=422,
                title="Validation Error",
                message=exc.errors().__repr__(),
            ).model_dump(),
        )

    @app.exception_handler(ResponseValidationError)
    async def handle_response_validation_error(_, exc: ResponseValidationError):  # type: ignore[override]
        # Log details internally; do not expose Pydantic internals to clients.
        logging.getLogger(__name__).exception("Response validation error")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code=500,
                title="Internal Server Error",
                message="An unexpected error occurred.",
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_, exc: Exception):  # type: ignore[override]
        logging.getLogger(__name__).exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code=500,
                title="Internal Server Error",
                message="An unexpected error occurred.",
            ).model_dump(),
        )


async def server_error_handler(_: Request, __: Exception):
    """Starlette ServerErrorMiddleware handler to force uniform JSON on 500s.

    This ensures that even in debug mode, we don't leak tracebacks to clients.
    """
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code=500,
            title="Internal Server Error",
            message="An unexpected error occurred.",
        ).model_dump(),
    )


__all__ = ["register_exception_handlers", "server_error_handler"]
