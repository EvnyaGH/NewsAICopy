from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware import Middleware
from sqlalchemy import text

from app.api.routes import api_router
from app.shared.config import settings, Settings
from app.shared.logging_config import setup_logging
from app.middleware import RequestContextMiddleware, SessionMiddleware
from app.shared.telemetry import init_otel
from app.exceptions.exception_handlers import register_exception_handlers, server_error_handler
from starlette.middleware.errors import ServerErrorMiddleware
import app.db.session as db_session
from fastapi.middleware.cors import CORSMiddleware
from app.shared.cache import init_redis, close_redis

DESCRIPTION = (
    "NewsAI backend serves resources over a clean FastAPI API. "
    "Background ingestion and AI processing run in a separate service. "
    "This service focuses on HTTP APIs, data access, and observability."
)

TAGS_METADATA = [
    {"name": "health", "description": "Service health endpoints."},
    {"name": "users", "description": "Operations to manage users."},
    {"name": "auth", "description": "Authentication: Simple JWT (login/logout)."},
]


def create_app(settings_override: Settings | None = None) -> FastAPI:
    # Allow tests or callers to override settings
    cfg = settings_override or settings
    # Configure logging early so startup logs are structured
    setup_logging(cfg.log_level)

    @asynccontextmanager
    async def lifespan(api: FastAPI):
        # Startup: quick connectivity check only (no schema creation)
        with db_session.engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Initialize OpenTelemetry if enabled
        if cfg.enable_otel:
            init_otel(api, service_name=cfg.app_name, endpoint=cfg.otel_endpoint)
            logging.getLogger(__name__).info("OpenTelemetry initialized")
        # Initialize Redis (Upstash or compatible) if configured
        await init_redis(api)
        yield
        # Shutdown: add cleanup here if needed
        await close_redis(api)

    svr = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        debug=cfg.debug,
        description=DESCRIPTION,
        openapi_tags=TAGS_METADATA,
        docs_url=cfg.docs_url,
        redoc_url=cfg.redoc_url,
        openapi_url=cfg.openapi_url,
        lifespan=lifespan,
        middleware=[
            Middleware(
                RequestContextMiddleware,
                header_name=cfg.request_id_header,
                log_max_body_bytes=cfg.log_max_body_bytes,
                log_request_headers=cfg.log_request_headers,
                log_response_headers=cfg.log_response_headers,
            ),
            Middleware(SessionMiddleware),
        ],
    )

    # Versioned API prefix
    svr.include_router(api_router, prefix="/api/v1")
    register_exception_handlers(svr)

    # Ensure unexpected errors return our uniform JSON payload, even in debug
    svr.add_middleware(ServerErrorMiddleware, handler=server_error_handler)

    # CORS
    if cfg.cors_origins:
        svr.add_middleware(
            CORSMiddleware,
            allow_origins=cfg.cors_origins,
            allow_credentials=cfg.cors_allow_credentials,
            allow_methods=cfg.cors_allow_methods,
            allow_headers=cfg.cors_allow_headers,
        )

    return svr


app = create_app()
