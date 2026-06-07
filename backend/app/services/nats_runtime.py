from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import json
from typing import Any

from app.core.config import Settings


NatsMessageHandler = Callable[["NatsMessage"], Awaitable[None]]


@dataclass(frozen=True)
class NatsMessage:
    topic: str
    payload: dict[str, object]


@dataclass(frozen=True)
class NatsOperationResult:
    status: str
    detail: str = ""


class InMemoryNatsClient:
    def __init__(self) -> None:
        self.handlers: dict[str, list[NatsMessageHandler]] = {}
        self.published_messages: list[NatsMessage] = []

    async def publish(self, topic: str, payload: dict[str, object]) -> None:
        message = NatsMessage(topic=topic, payload=payload)
        self.published_messages.append(message)
        for handler in self.handlers.get(topic, []):
            await handler(message)

    async def subscribe(self, topic: str, handler: NatsMessageHandler) -> None:
        self.handlers.setdefault(topic, []).append(handler)

    async def close(self) -> None:
        self.handlers.clear()


class NatsClientAdapter:
    def __init__(self, client: Any) -> None:
        self.client = client

    async def publish(self, topic: str, payload: dict[str, object]) -> None:
        await self.client.publish(topic, json.dumps(payload).encode("utf-8"))

    async def subscribe(self, topic: str, handler: NatsMessageHandler) -> None:
        async def _callback(message: Any) -> None:
            payload = json.loads(message.data.decode("utf-8"))
            await handler(NatsMessage(topic=topic, payload=payload))

        await self.client.subscribe(topic, cb=_callback)

    async def close(self) -> None:
        await self.client.close()


class NatsRuntime:
    def __init__(
        self,
        settings: Settings,
        client: InMemoryNatsClient | NatsClientAdapter | None = None,
        unavailable_reason: str = "",
    ) -> None:
        self.settings = settings
        self.client = client
        self.unavailable_reason = unavailable_reason

    @property
    def enabled(self) -> bool:
        return bool((self.settings.nats_url or "").strip())

    async def publish(self, topic: str, payload: dict[str, object]) -> NatsOperationResult:
        if not self.enabled:
            return NatsOperationResult(status="disabled")
        if self.client is None:
            return NatsOperationResult(status="unavailable", detail=self.unavailable_reason)

        try:
            await self.client.publish(topic, payload)
        except Exception as exc:
            return NatsOperationResult(status="unavailable", detail=str(exc))

        return NatsOperationResult(status="published")

    async def subscribe(self, topic: str, handler: NatsMessageHandler) -> NatsOperationResult:
        if not self.enabled:
            return NatsOperationResult(status="disabled")
        if self.client is None:
            return NatsOperationResult(status="unavailable", detail=self.unavailable_reason)

        try:
            await self.client.subscribe(topic, handler)
        except Exception as exc:
            return NatsOperationResult(status="unavailable", detail=str(exc))

        return NatsOperationResult(status="subscribed")

    async def close(self) -> None:
        if self.client is not None:
            await self.client.close()


async def create_nats_runtime(settings: Settings) -> NatsRuntime:
    nats_url = (settings.nats_url or "").strip()
    if not nats_url:
        return NatsRuntime(settings)
    if nats_url == "memory://":
        return NatsRuntime(settings, client=InMemoryNatsClient())

    try:
        import nats
    except ImportError as exc:
        return NatsRuntime(settings, unavailable_reason=f"nats package unavailable: {exc}")

    try:
        client = await nats.connect(
            nats_url,
            connect_timeout=settings.nats_timeout_seconds,
        )
    except Exception as exc:
        return NatsRuntime(settings, unavailable_reason=str(exc))

    return NatsRuntime(settings, client=NatsClientAdapter(client))
