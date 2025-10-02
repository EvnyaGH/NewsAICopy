from __future__ import annotations

from passlib.context import CryptContext


# Use bcrypt for strong, adaptive hashing. Passlib manages salts and parameters.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    return pwd_context.verify(password, encoded)
