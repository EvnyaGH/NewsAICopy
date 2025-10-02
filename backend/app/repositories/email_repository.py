from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends
from redis.asyncio import Redis

from app.shared.config import settings
from app.shared.cache import get_redis


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _expire_at(ttl_seconds: int) -> datetime:
    return _now() + timedelta(seconds=ttl_seconds)


def _key(token_hash: str) -> str:
    return f"ev:{token_hash}"


class EmailRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def _ttl_seconds(self) -> int:
        return max(60, int(settings.email_verification_expires_minutes) * 60)

    async def set(self, token: str, user_id: str, expires_at: int) -> None:
        await self.redis.set(_key(token), user_id, ex=expires_at)

    async def delete(self, token: str) -> None:
        await self.redis.delete(_key(token))

    async def get(self, token: str) -> str | None:
        email = await self.redis.get(_key(token))
        if not email:
            return None

        return email


def get_email_repository(redis: Redis = Depends(get_redis)) -> EmailRepository:
    return EmailRepository(redis)
