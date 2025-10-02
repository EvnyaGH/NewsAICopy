from __future__ import annotations

import logging
from typing import Any


def init_otel(app: Any, service_name: str, endpoint: str | None = None) -> None:
    """Initialize OpenTelemetry tracing and instrument FastAPI if available.

    This is a no-op if OpenTelemetry packages are not installed.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # type: ignore
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
    except Exception:
        logging.getLogger(__name__).info(
            "OpenTelemetry not installed; skipping OTel initialization"
        )
        return

    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)

    # Configure exporter (HTTP by default, can be directed by endpoint)
    exporter = OTLPSpanExporter(endpoint=endpoint) if endpoint else OTLPSpanExporter()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Instrument FastAPI and logging
    FastAPIInstrumentor().instrument_app(app)
    # Avoid overriding the format; trace IDs are injected via a logging filter
    LoggingInstrumentor().instrument(set_logging_format=False)
