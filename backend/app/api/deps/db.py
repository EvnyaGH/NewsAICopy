from typing import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session for request-scoped use."""
    yield from _get_db()

