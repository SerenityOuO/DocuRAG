from app.core.config import Settings
from app.schemas.auth import AuthUser
from app.schemas.rag import RagQueryResponse
from app.services.redis_runtime import RedisRuntime


class FakeRedisClient:
    def __init__(self) -> None:
        self.values: dict[str, str | int] = {}
        self.ttls: dict[str, int] = {}
        self.ping_called = False

    def ping(self) -> bool:
        self.ping_called = True
        return True

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.values[key] = value
        self.ttls[key] = ttl

    def get(self, key: str) -> str | None:
        value = self.values.get(key)
        return value if isinstance(value, str) else None

    def incr(self, key: str) -> int:
        value = int(self.values.get(key, 0)) + 1
        self.values[key] = value
        return value

    def expire(self, key: str, ttl: int) -> None:
        self.ttls[key] = ttl

    def ttl(self, key: str) -> int:
        return self.ttls.get(key, -1)


def test_redis_runtime_disabled_fallback_keeps_calls_allowed() -> None:
    runtime = RedisRuntime(Settings(redis_url=None))

    assert runtime.health().status == "disabled"
    assert runtime.cache_session("token", AuthUser(username="admin", display_name="Admin", role="admin")).status == "disabled"
    assert runtime.get_query_cache("cache-key").status == "disabled"

    rate_limit = runtime.check_rate_limit("rag-query:anonymous", limit=1, window_seconds=60)

    assert rate_limit.allowed is True
    assert rate_limit.status == "disabled"


def test_redis_session_cache_hashes_token_and_stores_user_payload() -> None:
    client = FakeRedisClient()
    runtime = RedisRuntime(Settings(redis_url="redis://localhost:6379/0"), client=client)
    user = AuthUser(username="admin", display_name="Demo Admin", role="admin")

    result = runtime.cache_session("raw-token", user)

    assert result.status == "stored"
    [key] = list(client.values)
    assert key.startswith("docurag:session:")
    assert "raw-token" not in key
    assert client.values[key] == user.model_dump_json()
    assert client.ttls[key] == 3600


def test_redis_query_cache_round_trip_uses_response_schema() -> None:
    client = FakeRedisClient()
    runtime = RedisRuntime(Settings(redis_url="redis://localhost:6379/0"), client=client)
    response = RagQueryResponse(answer="cached answer", citations=[], retrieved_chunks=[])

    write_result = runtime.set_query_cache("cache-key", response)
    read_result = runtime.get_query_cache("cache-key")

    assert write_result.status == "stored"
    assert read_result.status == "hit"
    assert read_result.response == response
    assert client.ttls["docurag:rag:query:cache-key"] == 60


def test_redis_rate_limit_blocks_after_limit() -> None:
    client = FakeRedisClient()
    runtime = RedisRuntime(
        Settings(redis_url="redis://localhost:6379/0", redis_rate_limit_per_minute=2),
        client=client,
    )

    first = runtime.check_rate_limit("rag-query:admin", limit=2, window_seconds=60)
    second = runtime.check_rate_limit("rag-query:admin", limit=2, window_seconds=60)
    third = runtime.check_rate_limit("rag-query:admin", limit=2, window_seconds=60)

    assert first.allowed is True
    assert first.status == "ok"
    assert first.remaining == 1
    assert second.allowed is True
    assert second.remaining == 0
    assert third.allowed is False
    assert third.status == "limited"
    assert third.retry_after_seconds == 60


def test_redis_unavailable_falls_back_without_blocking_rate_limit() -> None:
    runtime = RedisRuntime(
        Settings(redis_url="redis://localhost:6379/0"),
        unavailable_reason="redis package unavailable",
    )

    health = runtime.health()
    rate_limit = runtime.check_rate_limit("rag-query:admin", limit=2, window_seconds=60)

    assert health.status == "unavailable"
    assert "redis package unavailable" in health.detail
    assert rate_limit.allowed is True
    assert rate_limit.status == "unavailable"
