from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.shared.config import settings


async def init_redis(app) -> None:
    app.state.redis = None
    if not settings.redis_url:
        # Hard fail: service requires Redis for auth (refresh tokens and revocation)
        raise RuntimeError("REDIS_URL not set; Redis is required for authentication")
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.ping()
    except Exception as e:
        logging.getLogger(__name__).error("Redis ping failed: %s", e)
        # Propagate the error so startup fails fast
        raise
    app.state.redis = client


async def close_redis(app) -> None:
    redis: Redis | None = getattr(app.state, "redis", None)
    if redis is not None:
        await redis.aclose()


def get_redis(request: Request) -> Redis:
    redis: Redis | None = getattr(request.app.state, "redis", None)
    if redis is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis not configured")
    return redis


RedisDep = Annotated[Redis, Depends(get_redis)]
