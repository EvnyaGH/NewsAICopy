# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# System deps (minimal). Add build tools only if needed.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy dependency manifests first for better layer caching
COPY pyproject.toml uv.lock ./

# Create virtualenv and install deps (prod only)
RUN uv venv && uv sync --frozen --no-dev

# Copy application source
COPY app ./app

COPY README.md .

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Ensure entrypoint is executable inside the image
COPY --chmod=0755 docker-entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "app.main:app"]
