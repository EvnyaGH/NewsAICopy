## 📰 NewsAI Backend

A Python backend for the NewsAI platform. Built on FastAPI for high‑performance, type‑safe APIs; SQLAlchemy for ORM
with Alembic for schema versioning; and Pydantic for validation. It runs behind Gunicorn/Uvicorn in production, uses
`uv` for fast and reproducible dependency management, and supports structured JSON logging plus optional OpenTelemetry
tracing. Responses follow a consistent envelope for easier client consumption and observability.

Why this stack: FastAPI provides an async, schema‑first developer experience with automatic OpenAPI; SQLAlchemy 2.x
offers a modern, type‑friendly ORM over multiple databases. Gunicorn manages
resilient multi‑worker processes using Uvicorn for raw ASGI speed; and `uv` makes dependency management fast and
reproducible across local and CI.

## 🚀 Key Features

* Robust API: Built with FastAPI for high-performance and clear endpoints.
* Separation of Concerns: Background ingestion/AI processing runs in a separate service.
* Layered Architecture: Clear separation of concerns with services, repositories, and models.
* Scalable Storage: Postgres for metadata and state, object storage for artifacts.
* Schema Management: Alembic for smooth database migrations.
* Observability: JSON logs with request/trace IDs; optional OpenTelemetry.
* Testing: Pytest suite with Makefile target (`make test`).

## 📁 Directory Structure

```code
.
├── app/                  # 🧩 Main application code
│   ├── api/              # ⚡ API endpoints
│   │   ├── routes/       # HTTP routes/handlers
│   │   └── deps/         # FastAPI dependencies
│   ├── db/               # 🗄️ SQLAlchemy setup
│   ├── models/           # 📊 SQLAlchemy ORM models
│   ├── schemas/          # 📝 Pydantic models for data validation
│   ├── repositories/     # 📦 Data access layer
│   ├── services/         # 🧠 Business logic and application services
│   ├── shared/           # 🤝 Shared utilities and clients
│   │   ├── cache/        # Redis cache client
│   │   └── emails/       # Email client and templates
│   └── main.py           # 🚀 FastAPI application entry point
├── tests/                # ✅ Pytest suite
├── .env.example          # 📋 Template for environment variables
├── Dockerfile            # 🐳 Production container image
├── docker-compose.yml    # 🐳 Local Postgres service
├── Makefile              # 🛠️ Handy commands for development
└── pyproject.toml        # 📦 Project dependencies and metadata
```

## 🛠️ Setup

### 1. Prerequisites

Before you begin, make sure you have these installed:

* **Python 3.10+**: The core language for this project.
* **`uv` (package/dependency manager)**: A super-fast next-gen package manager. Get it
  here: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
* **Postgres**: For storing data.

You can use the docker-compose file for this.

### 2. Create a Virtual Environment & Install Dependencies

It's crucial to use a virtual environment to keep your project dependencies isolated and clean. This prevents conflicts
with other Python projects on your machine. Since you won't be committing it to Git, you'll create it directly in your
project root.

1. **Navigate to your project directory**:
   ```bash
   cd backend
   ```

2. **Create the virtual environment**:
   `uv` makes this super simple! This command will create a `.venv` directory in your current folder.
   ```bash
   uv venv
   ```

3. **Activate your virtual environment**:
   You need to "enter" the virtual environment so that any `python` or `uv` commands use the packages installed within
   it, not your global Python installation.
    * **On macOS/Linux**:
      ```bash
      source .venv/bin/activate
      ```
    * **On Windows (Command Prompt)**:
      ```bash
      .venv\Scripts\activate.bat
      ```
    * **On Windows (PowerShell)**:
      ```bash
      .venv\Scripts\Activate.ps1
      ```
   You'll notice your terminal prompt changes, usually with `(.venv)` at the beginning, indicating the virtual
   environment is active.

4. **Install project dependencies**:
   With your virtual environment active, `uv sync` will install all the packages listed in `pyproject.toml` into your
   `.venv`.
   ```bash
   uv sync
   ```

   **Note**: You must activate your virtual environment *every time* you open a new terminal session to work on this
   project. If you close your terminal, you'll need to run `source .venv/bin/activate` (or its Windows equivalent)
   again.

### 3. Environment Variables

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```
2. **Edit `.env`**: Open the newly created `.env` file and adjust the variables to your local setup.

    * `DATABASE_URL`:
        * **SQLite (default for local dev)**: `sqlite:///./app.db`
        * **Postgres (via Docker Compose example)**: Refer to your `docker-compose.yml` for the correct URL.
    * Background processing config is managed in the separate worker service.
    * Logging and Observability:
        * `LOG_LEVEL` (default `INFO`)
        * `REQUEST_ID_HEADER` (default `X-Request-ID`)
        * `LOG_MAX_BODY_BYTES` (default `8192`)
        * `LOG_REQUEST_HEADERS` (default `true`)
        * `LOG_RESPONSE_HEADERS` (default `true`)
        * `DISABLE_UVICORN_ACCESS` (default `true`)
        * `ENABLE_OTEL` (default `false`)
        * `OTEL_ENDPOINT` (e.g. `http://localhost:4318`)
    * CORS:
        * `CORS_ORIGINS` (JSON array, e.g., `["http://localhost:3000"]`)
        * `CORS_ALLOW_CREDENTIALS` (default `true`)
        * `CORS_ALLOW_METHODS` (default `["*"]`)
        * `CORS_ALLOW_HEADERS` (default `["*"]`)

## ▶️ Run the Application

Make sure your virtual environment is activated (`source .venv/bin/activate`) before running any commands.

* **API (Development Mode)**: Starts the FastAPI server with auto-reloading for quick development.
  ```bash
  uv run uvicorn app.main:app --reload
  ```
* **Using `Makefile` targets (Recommended)**:
  ```bash
  make run-api   # Start the API
  make up        # Bring up all services (e.g., with Docker Compose)
  make down      # Tear down all services
  ```

## 🐳 Docker

Build a production image and run it with your `.env`:

```bash
docker build -t newsai-backend .
docker run --env-file .env -p 8000:8000 newsai-backend
```

Notes:

- The container entrypoint runs `alembic upgrade head` automatically before launching the API.
- The API runs with Gunicorn + Uvicorn workers and logs to stdout in JSON.

## Running with HTTPS

* Edit your `/etc/hosts` file to include the following
  ```bash
  127.0.0.1       api.zara.com # for be
  127.0.0.1       zara.com # for fe
  ```
* Run the following command in the root `/NewsAI` not `/NewsAI/backend`
  ```bash
  docker compose --profile setup up certificate-generator
  ```
  
* Run the app using the `Makefile` command
  ```bash
  make run run-api-https
  ```
  
* Now you can use `https` locally with `https://api.zara.com:8443`

## ✅ Testing

Run the test suite (pytest):

```bash
make test
```

Notes:

- Tests spin up the FastAPI app with a temporary SQLite database (no external services required).
- The suite covers health checks and CORS headers.
- You can run directly: `uv run pytest -q`.

## 🚀 PyCharm Setup (Recommended for IDE Users)

For a smooth development experience in PyCharm:

1. **Mark `backend/app` as Sources Root**:
    * Right-click on the `app` directory within your project.
    * Select `Mark Directory As` → `Sources Root`.
      This helps PyCharm resolve imports correctly (e.g., `from app.api import ...`).

2. **Use interpreter from `backend/.venv`**:
    * Go to `File` → `Settings` (or `PyCharm` → `Preferences` on macOS) → `Project: NewsAI Backend` →
      `Python Interpreter`.
    * Click on the gear icon ⚙️ → `Add...`
    * Select `Virtualenv Environment` → `Existing environment`.
    * Click the `...` button and navigate to your `backend/.venv/bin/python` (or `backend\.venv\Scripts\python.exe` on
      Windows).
    * Click `OK` to apply.

3. **Working Directory for Run Configurations**:
    * Ensure the `Working directory` for all your run configurations (API, Alembic, Celery) is set to the `backend`
      project root.

4. **API Run Configuration**:
    * **Module**: `uvicorn`
    * **Parameters**: `app.main:app --reload`

5. **Alembic Run Configuration**:
    * **Module**: `alembic`
    * **Parameters**: e.g., `upgrade head`

## 🌐 API Docs

- Swagger available at path: `/api/v1/docs`


### 🤝 Example API Call

Uniform response envelope:

- Success: `{ "code": 201, "data": { ... } }`
- Error: `{ "code": 409, "title": "Conflict", "message": "..." }`


### Resend Email Service

This project uses [Resend](https://resend.com) for sending transactional emails (e.g., email verification). To enable this service locally or in production, you need to configure your Resend account and API key.

1.  **Register on Resend**:
    *   Go to [https://resend.com](https://resend.com) and create a free account.

2.  **Set Environment Variables**:
    *   In your `.env` file, add the following variables:
        *   `RESEND_API_KEY`: Your API key from the Resend dashboard.
        *   `RESEND_SENDER_EMAIL`: The email address you verified with Resend to send emails from. This should be the email you used to register.

    Example `.env` configuration:
    ```env
    RESEND_API_KEY=re_xxxxxxxxxxxxxxxx
    RESEND_SENDER_EMAIL=you@example.com
    ```


## 📚 Key Libraries Used

| Library                | Description                                                                                               | Documentation                                             |
|:-----------------------|:----------------------------------------------------------------------------------------------------------|:----------------------------------------------------------|
| FastAPI                | Async, type‑driven web framework with automatic OpenAPI docs and great developer ergonomics.              | https://fastapi.tiangolo.com/                             |
| Pydantic v2            | Strict, typed models for request/response validation and serialization.                                   | https://docs.pydantic.dev/latest/                         |
| pydantic‑settings      | Type‑safe configuration loaded from environment and .env files.                                           | https://docs.pydantic.dev/latest/usage/pydantic_settings/ |
| SQLAlchemy 2.0         | Modern ORM/Core with clean async‑ready patterns and type annotations.                                     | https://docs.sqlalchemy.org/en/20/                        |
| psycopg[binary]        | High‑performance PostgreSQL driver for production deployments targeting Postgres.                         | https://www.psycopg.org/psycopg3/docs/                    |
| Uvicorn[standard]      | Lightning‑fast ASGI server used as the worker runtime under Gunicorn.                                     | https://www.uvicorn.org/                                  |
| Gunicorn               | Production process manager supervising multiple Uvicorn workers; handles timeouts, restarts, and signals. | https://gunicorn.org/                                     |
| uv                     | Ultra‑fast dependency manager/runner used in Docker/Makefile for reproducible installs.                   | https://docs.astral.sh/uv/                                |
| OpenTelemetry SDK+OTLP | Vendor‑neutral tracing/metrics; exports to any OTLP‑compatible backend.                                   | https://opentelemetry.io/docs/                            |
| OTel FastAPI instr.    | Auto‑instrumentation for FastAPI routes to capture spans/attributes.                                      | https://opentelemetry-python-contrib.readthedocs.io/      |
| OTel logging instr.    | Enriches Python logging records with trace context for correlation.                                       | https://opentelemetry-python-contrib.readthedocs.io/      |
| Pytest                 | Test framework for unit/integration tests with succinct, expressive assertions.                           | https://docs.pytest.org/                                  |

## 👀 Observability

- JSON logs with fields: `ts`, `level`, `logger`, `msg`, `request_id`, `trace_id`, `span_id`.
- Structured HTTP access logs include: method, path, query, client, status, duration_ms, request/response bodies
  (JSON or size), and request/response headers (sensitive redacted). A request ID is generated when missing and
  returned as `X-Request-ID`.
- Optional OpenTelemetry tracing can be enabled via `ENABLE_OTEL=true` and `OTEL_ENDPOINT`.

## 🌐 CORS

Configure CORS via environment variables. Example allow a local frontend:

```env
CORS_ORIGINS=["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

## 🎨 Architecture Notes

* Repositories and Services: Provide clear boundaries for data access and business logic, significantly improving
  testability and maintainability.
* Uniform Responses: All successes return `{ code, data }`. All errors return `{ code, title, message }`.
  - Custom `APIError` subclasses: `title` is the exception class name (e.g., `ConflictError`).
  - Starlette/FastAPI `HTTPException`: titled `HTTP Error` with its status and detail.
  - Pydantic `RequestValidationError`: titled `Validation Error` (422).
  - Any other exception: titled `Internal Server Error` (500) with a generic message, full details in logs.

## ⚠️ Troubleshooting

- Import errors for app:
  Ensure your Working Directory in your IDE/terminal is the backend project root.
  In PyCharm, confirm backend/app is marked as a Sources Root.
- Missing packages:
  Activate your virtual environment (source .venv/bin/activate).
  Run uv sync to install all dependencies.
- Alembic import errors:
  Always run Alembic commands from the backend project root.
  Alternatively, set your PYTHONPATH environment variable to include the backend directory (e.g., export PYTHONPATH=$(
  pwd)).
