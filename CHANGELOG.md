# Changelog

All notable changes to this project are documented here.

## Sprint 1

- Wiki
  - Project background
  - Personas
  - Motivation model
  - Glossary
  - Functional requirements (FR)
  - Non‑functional requirements (NFR)
  - User stories
  - Technology constraints and choices
  - Stakeholder identification
  - Roles & responsibilities
  - Team
  - Communication plan
  - Risks
  - QA & test plan

- Backend
  - Added initial backend structure (FastAPI app, services, repositories, models, Alembic migrations, tests, Makefile, Docker assets).
  - Established layered architecture: API routers → services → repositories → SQLAlchemy models/schemas.
  - Database via SQLAlchemy + Alembic; default local SQLite with Postgres-ready configuration.
  - Background processing with Celery + Redis, including optional scheduler (beat).
  - Observability: structured JSON logging with request IDs and optional OpenTelemetry tracing.
  - Developer workflow: `uv` for deps, Makefile targets, Dockerfile and docker-compose for local services, pytest suite.
