import tempfile

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.shared.config import Settings
import app.db.session as db_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base


@pytest.fixture(scope="session")
def test_db_url() -> str:
    # Use a temporary SQLite file for realistic behavior
    tmp = tempfile.NamedTemporaryFile(prefix="test_db_", suffix=".db", delete=False)
    tmp.close()
    return f"sqlite:///{tmp.name}"


@pytest.fixture(scope="session")
def app_fixture(test_db_url: str):
    # Override DB engine/session for tests
    engine = create_engine(test_db_url, future=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

    # Create tables for tests only
    Base.metadata.create_all(bind=engine)

    # Monkeypatch the global engine/session used by the app
    db_session.engine = engine
    db_session.SessionLocal = TestingSessionLocal

    test_settings = Settings(
        database_url=test_db_url,
        enable_otel=False,
        cors_origins=["http://example.com"],
    )

    app = create_app(test_settings)
    yield app


@pytest.fixture()
def client(app_fixture):
    with TestClient(app_fixture) as c:
        yield c
