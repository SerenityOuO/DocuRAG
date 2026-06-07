from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from app.core.config import Settings
from app.schemas.auth import AuthUser
from app.schemas.rag import RagQueryResponse


@dataclass(frozen=True)
class RedisHealth:
    status: str
    detail: str = ""


@dataclass(frozen=True)
class RedisWriteResult:
    status: str
    detail: str = ""


@dataclass(frozen=True)
class RedisCacheReadResult:
    status: str
    response: RagQueryResponse | None = None
    detail: str = ""


@dataclass(frozen=True)
class RedisRateLimitResult:
    allowed: bool
    status: str
    limit: int
    remaining: int | None = None
    retry_after_seconds: int | None = None
    detail: str = ""


class RedisRuntime:
    def __init__(
        self,
        settings: Settings,
        client: Any | None = None,
        unavailable_reason: str = "",
    ) -> None:
        self.settings = settings
        self.client = client
        self.unavailable_reason = unavailable_reason

    @property
    def enabled(self) -> bool:
        return bool((self.settings.redis_url or "").strip())

    @property
    def available(self) -> bool:
        return self.enabled and self.client is not None and not self.unavailable_reason

    def health(self) -> RedisHealth:
        if not self.enabled:
            return RedisHealth(status="disabled")
        if self.client is None:
            return RedisHealth(status="unavailable", detail=self.unavailable_reason or "Redis client is unavailable.")

        try:
            self.client.ping()
        except Exception as exc:  # pragma: no cover - real Redis failure shape depends on redis-py.
            return RedisHealth(status="unavailable", detail=str(exc))

        return RedisHealth(status="ok")

    def cache_session(self, token: str, user: AuthUser) -> RedisWriteResult:
        if not self.enabled:
            return RedisWriteResult(status="disabled")
        if self.client is None:
            return RedisWriteResult(status="unavailable", detail=self.unavailable_reason)

        key = f"docurag:session:{sha256(token.encode('utf-8')).hexdigest()}"
        payload = user.model_dump_json()
        try:
            self.client.setex(key, self.settings.redis_session_ttl_seconds, payload)
        except Exception as exc:
            return RedisWriteResult(status="unavailable", detail=str(exc))

        return RedisWriteResult(status="stored")

    def get_query_cache(self, cache_key: str) -> RedisCacheReadResult:
        if not self.enabled:
            return RedisCacheReadResult(status="disabled")
        if self.client is None:
            return RedisCacheReadResult(status="unavailable", detail=self.unavailable_reason)

        try:
            payload = self.client.get(f"docurag:rag:query:{cache_key}")
        except Exception as exc:
            return RedisCacheReadResult(status="unavailable", detail=str(exc))

        if payload is None:
            return RedisCacheReadResult(status="miss")

        try:
            response = RagQueryResponse.model_validate_json(payload)
        except ValueError as exc:
            return RedisCacheReadResult(status="invalid", detail=str(exc))

        return RedisCacheReadResult(status="hit", response=response)

    def set_query_cache(self, cache_key: str, response: RagQueryResponse) -> RedisWriteResult:
        if not self.enabled:
            return RedisWriteResult(status="disabled")
        if self.client is None:
            return RedisWriteResult(status="unavailable", detail=self.unavailable_reason)

        try:
            self.client.setex(
                f"docurag:rag:query:{cache_key}",
                self.settings.redis_query_cache_ttl_seconds,
                response.model_dump_json(),
            )
        except Exception as exc:
            return RedisWriteResult(status="unavailable", detail=str(exc))

        return RedisWriteResult(status="stored")

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RedisRateLimitResult:
        if limit <= 0 or window_seconds <= 0:
            return RedisRateLimitResult(allowed=True, status="disabled", limit=limit)
        if not self.enabled:
            return RedisRateLimitResult(allowed=True, status="disabled", limit=limit)
        if self.client is None:
            return RedisRateLimitResult(
                allowed=True,
                status="unavailable",
                limit=limit,
                detail=self.unavailable_reason,
            )

        redis_key = f"docurag:rate:{key}"
        try:
            count = int(self.client.incr(redis_key))
            if count == 1:
                self.client.expire(redis_key, window_seconds)
            ttl = int(self.client.ttl(redis_key))
            if ttl < 0:
                self.client.expire(redis_key, window_seconds)
                ttl = window_seconds
        except Exception as exc:
            return RedisRateLimitResult(allowed=True, status="unavailable", limit=limit, detail=str(exc))

        remaining = max(0, limit - count)
        if count > limit:
            return RedisRateLimitResult(
                allowed=False,
                status="limited",
                limit=limit,
                remaining=remaining,
                retry_after_seconds=ttl,
            )

        return RedisRateLimitResult(
            allowed=True,
            status="ok",
            limit=limit,
            remaining=remaining,
            retry_after_seconds=ttl,
        )


def create_redis_runtime(settings: Settings) -> RedisRuntime:
    redis_url = (settings.redis_url or "").strip()
    if not redis_url:
        return RedisRuntime(settings)

    try:
        from redis import Redis
    except ImportError as exc:
        return RedisRuntime(settings, unavailable_reason=f"redis package unavailable: {exc}")

    try:
        client = Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=settings.redis_timeout_seconds,
            socket_timeout=settings.redis_timeout_seconds,
        )
    except Exception as exc:
        return RedisRuntime(settings, unavailable_reason=str(exc))

    return RedisRuntime(settings, client=client)
