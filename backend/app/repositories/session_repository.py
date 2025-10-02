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


def _key(session_id: str) -> str:
    return f"sess:{session_id}"


@dataclass
class SessionData:
    user_id: str
    roles: list[str]
    expires_at: datetime

    def to_json(self) -> str:
        return json.dumps(
            {
                "user_id": self.user_id,
                "roles": self.roles,
                # Store as ISO 8601
                "expires_at": self.expires_at.isoformat(),
            }
        )

    @staticmethod
    def from_json(s: str) -> "SessionData":
        obj = json.loads(s)
        return SessionData(
            user_id=obj["user_id"],
            roles=list(obj.get("roles", [])),
            expires_at=datetime.fromisoformat(obj["expires_at"]),
        )


class SessionRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def _ttl_seconds(self) -> int:
        return max(60, int(settings.session_expires_minutes) * 60)

    async def create(self, user_id: str, roles: list[str]) -> tuple[str, int, SessionData]:
        sid = secrets.token_urlsafe(24)
        ttl = self._ttl_seconds()
        data = SessionData(user_id=user_id, roles=roles, expires_at=_expire_at(ttl))
        await self.redis.set(_key(sid), data.to_json(), ex=ttl)
        return sid, ttl, data

    async def get(self, sid: str) -> Optional[SessionData]:
        raw = await self.redis.get(_key(sid))
        if not raw:
            return None
        try:
            return SessionData.from_json(raw)
        except Exception:
            return None

    async def delete(self, sid: str) -> None:
        await self.redis.delete(_key(sid))


def get_session_repository(redis: Redis = Depends(get_redis)) -> SessionRepository:
    return SessionRepository(redis)
