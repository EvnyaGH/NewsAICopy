from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any, Iterable, cast

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.shared.logging_config import request_id_ctx_var


def _maybe_json(data: bytes, max_len: int) -> Any:
    if len(data) > max_len:
        return {"truncated": True, "size": len(data)}
    try:
        return json.loads(data.decode("utf-8"))
    except Exception:
        text = data.decode("utf-8", errors="replace")
        if len(text) > max_len:
            return {"truncated": True, "size": len(text)}
        return text


def _redact(obj: Any) -> Any:
    SENSITIVE = {"password", "token", "access_token", "authorization", "secret", "api_key"}
    try:
        if isinstance(obj, dict):
            return {k: ("***" if k.lower() in SENSITIVE else _redact(v)) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_redact(v) for v in obj]
    except Exception:
        pass
    return obj


SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
    "proxy-authorization",
}


def _redact_headers(items: Iterable[tuple[str, str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in items:
        if k.lower() in SENSITIVE_HEADERS:
            out[k] = "***"
        else:
            out[k] = v
    return out


class RequestContextMiddleware(BaseHTTPMiddleware):
    """HTTP middleware that manages a request ID and structured access logging.

    - Reads `X-Request-ID` (configurable) or generates a new UUID.
    - Stores it in a context so logs include it.
    - Adds `X-Request-ID` to the response headers.
    - Logs method, path, query params, request/response JSON bodies (safe), status, duration, client.
    """

    def __init__(
        self,
        app,
        header_name: str = "X-Request-ID",
        log_max_body_bytes: int = 8192,
        log_request_headers: bool = True,
        log_response_headers: bool = True,
    ) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.header_name = header_name
        self.log_max_body_bytes = log_max_body_bytes
        self.log_request_headers = log_request_headers
        self.log_response_headers = log_response_headers
        self.log = logging.getLogger("app.request")

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = request.headers.get(self.header_name) or uuid.uuid4().hex
        token = request_id_ctx_var.set(request_id)
        start = time.perf_counter()

        try:
            raw_body = await request.body()
        except Exception:
            raw_body = b""

        response: Response = await call_next(request)

        # Capture response body (except for 204/304 where bodies are not allowed)
        chunks: list[bytes] = []
        body_bytes = b""
        if response.status_code in (204, 304):
            # Do not consume/rebuild; ensure no body is logged
            body_bytes = b""
        elif getattr(response, "body_iterator", None) is not None:
            async for chunk in response.body_iterator:  # type: ignore[attr-defined]
                chunks.append(chunk)
            body_bytes = b"".join(chunks)
            new_response = Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
                background=response.background,
            )
            response = new_response
        else:
            try:
                body_bytes = response.body  # type: ignore[attr-defined]
            except Exception:
                body_bytes = b""

        duration_ms = (time.perf_counter() - start) * 1000.0
        # Help static type checkers accept the rounded float
        duration_ms_val = cast(float, round(duration_ms, 2))

        req_content_type = request.headers.get("content-type", "")
        res_content_type = response.headers.get("content-type", "")
        request_payload = None
        response_payload = None

        if "application/json" in req_content_type and raw_body:
            request_payload = _redact(_maybe_json(raw_body, self.log_max_body_bytes))
        elif raw_body:
            request_payload = {"size": len(raw_body)}

        if "application/json" in res_content_type and body_bytes:
            response_payload = _maybe_json(body_bytes, self.log_max_body_bytes)
        elif body_bytes:
            response_payload = {"size": len(body_bytes)}

        extra = {
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
            "status": response.status_code,
            "duration_ms": duration_ms_val,
            "client": request.client.host if request.client else "-",
            "request": request_payload,
            "response": response_payload,
        }
        if self.log_request_headers:
            extra["request_headers"] = _redact_headers(request.headers.items())
        if self.log_response_headers:
            extra["response_headers"] = _redact_headers(response.headers.items())
        self.log.info("access", extra=extra)

        response.headers[self.header_name] = request_id
        request_id_ctx_var.reset(token)
        return response


__all__ = ["RequestContextMiddleware"]