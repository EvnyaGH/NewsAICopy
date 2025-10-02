from __future__ import annotations

import contextvars
import datetime as _dt
import json
import logging
from typing import Any

# Context var for per-request correlation
request_id_ctx_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        record.request_id = request_id_ctx_var.get() or "-"
        return True


class TraceContextFilter(logging.Filter):
    def __init__(self) -> None:
        super().__init__()
        try:
            from opentelemetry import trace  # type: ignore

            self._trace = trace
        except Exception:
            self._trace = None

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        trace_id = span_id = "-"
        try:
            if self._trace is not None:
                span = self._trace.get_current_span()
                ctx = span.get_span_context() if span else None
                if ctx and ctx.is_valid:
                    trace_id = format(ctx.trace_id, "032x")
                    span_id = format(ctx.span_id, "016x")
        except Exception:
            # Never let logging crash the app
            pass
        record.trace_id = trace_id
        record.span_id = span_id
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        payload: dict[str, Any] = {
            # timezone-aware UTC timestamp
            "ts": _dt.datetime.fromtimestamp(record.created, _dt.timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "trace_id": getattr(record, "trace_id", "-"),
            "span_id": getattr(record, "span_id", "-"),
        }
        # Include additional custom attributes from `extra={...}`
        standard = {"name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module", "exc_info",
                    "exc_text", "stack_info", "lineno", "funcName", "created", "msecs", "relativeCreated", "thread",
                    "threadName", "processName", "process", "message", "request_id", "trace_id", "span_id"}
        for key, value in record.__dict__.items():
            if key not in standard and not key.startswith("_"):
                # Avoid overwriting existing keys
                if key not in payload:
                    payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)
        return json.dumps(payload, default=str)


from app.shared.config import settings


def setup_logging(level: str = "INFO") -> None:
    """Configure root and uvicorn loggers for JSON output with correlation fields.

    This is safe to call multiple times; it will replace the root handlers.
    """
    root = logging.getLogger()

    # Build handler with filters
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    handler.addFilter(TraceContextFilter())

    # Apply to root
    root.handlers = [handler]
    root.setLevel(level)

    # Configure Uvicorn loggers to propagate to root for consistent formatting
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []  # remove uvicorn default handlers
        lg.propagate = True
        lg.setLevel(level)
    # Silence Uvicorn access logs, the request middleware handles access logging
    logging.getLogger("uvicorn.access").disabled = settings.disable_uvicorn_access


__all__ = [
    "setup_logging",
    "request_id_ctx_var",
]
