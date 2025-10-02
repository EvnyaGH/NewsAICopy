.PHONY: up down logs run-api run-api-https run-api-all makemigration migrate psql lint-style test docker docker-build docker-run

# Docker image/container configuration (overridable)
IMAGE ?= newsai-backend
TAG ?= latest
CONTAINER ?= $(IMAGE)

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

run-api:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


run-api-https:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8443 --ssl-keyfile certs/api.zara.com-key.pem --ssl-certfile certs/api.zara.com.pem

run-api-all:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8443 --ssl-keyfile certs/api.zara.com-key.pem --ssl-certfile certs/api.zara.com.pem



psql:
	docker compose exec -it db psql -U $POSTGRES_USER -d $POSTGRES_DB



test:
	uv run pytest

seed-dev:
	uv run python scripts/seed_dev.py

# Build the Docker image from the Dockerfile
docker-build:
	docker build -t $(IMAGE):$(TAG) .

# Run the app container mapping port 8000; uses .env if present
docker-run:
	-@test -f .env && EF="--env-file .env" || EF=""; \
		docker run --rm -p 8000:8000 $EF --name $(CONTAINER) $(IMAGE):$(TAG)

# Convenience: build then run
docker: docker-build docker-run
