import json
import socket
from typing import Any
import urllib.error
import urllib.request

import pytest

from app.core.config import Settings
from app.services.embedding import (
    EmbeddingProviderDisabledError,
    EmbeddingProviderError,
    OllamaEmbeddingProvider,
    create_embedding_provider,
)


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.closed = False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def close(self) -> None:
        self.closed = True


def test_create_embedding_provider_returns_disabled_provider_without_env() -> None:
    provider = create_embedding_provider(Settings(embedding_provider=None))

    health = provider.check_health()

    assert health.enabled is False
    assert health.available is False
    with pytest.raises(EmbeddingProviderDisabledError, match="DOCURAG_EMBEDDING_PROVIDER=ollama"):
        provider.embed("hello")


def test_ollama_embed_sends_native_embed_request_and_parses_response() -> None:
    captured: dict[str, Any] = {}

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {
                "model": "qwen3-embedding:0.6b",
                "embeddings": [[0.125, -0.25, 1]],
                "prompt_eval_count": 4,
                "total_duration": 10_000_000,
                "load_duration": 2_000_000,
            }
        )

    provider = OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434/",
        model="qwen3-embedding:0.6b",
        timeout_seconds=5,
        transport=transport,
    )

    result = provider.embed("  hello  ")

    assert captured == {
        "url": "http://127.0.0.1:11434/api/embed",
        "method": "POST",
        "timeout": 5,
        "body": {
            "model": "qwen3-embedding:0.6b",
            "input": "hello",
        },
    }
    assert result.embedding == [0.125, -0.25, 1.0]
    assert result.dimension == 3
    assert result.model == "qwen3-embedding:0.6b"
    assert result.prompt_tokens == 4
    assert result.total_duration_ms == 10.0
    assert result.load_duration_ms == 2.0


def test_ollama_embedding_health_reports_model_available() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        assert request.full_url == "http://127.0.0.1:11434/api/tags"
        assert request.get_method() == "GET"
        return FakeResponse({"models": [{"name": "qwen3-embedding:0.6b"}]})

    provider = OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        transport=transport,
    )

    health = provider.check_health()

    assert health.enabled is True
    assert health.available is True
    assert health.models == ["qwen3-embedding:0.6b"]


def test_ollama_embedding_health_reports_missing_model() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        return FakeResponse({"models": [{"name": "qwen3.5:4b"}]})

    provider = OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        transport=transport,
    )

    health = provider.check_health()

    assert health.enabled is True
    assert health.available is False
    assert "qwen3-embedding:0.6b" in health.message
    assert health.models == ["qwen3.5:4b"]


def test_ollama_embed_reports_timeout() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        raise socket.timeout("timed out")

    provider = OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        timeout_seconds=1,
        transport=transport,
    )

    with pytest.raises(EmbeddingProviderError, match="timed out after 1.0s"):
        provider.embed("hello")


def test_ollama_embed_reports_connection_error() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        raise urllib.error.URLError(ConnectionRefusedError("connection refused"))

    provider = OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        transport=transport,
    )

    with pytest.raises(EmbeddingProviderError, match="Cannot connect to Ollama"):
        provider.embed("hello")


def test_ollama_embed_reports_http_error_body() -> None:
    error = urllib.error.HTTPError(
        url="http://127.0.0.1:11434/api/embed",
        code=404,
        msg="not found",
        hdrs=None,
        fp=FakeResponse({"error": "model 'qwen3-embedding:0.6b' not found"}),
    )

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        raise error

    provider = OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        transport=transport,
    )

    with pytest.raises(EmbeddingProviderError, match="qwen3-embedding:0.6b"):
        provider.embed("hello")


def test_ollama_embed_reports_malformed_response_without_embeddings() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        return FakeResponse({"model": "qwen3-embedding:0.6b"})

    provider = OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        transport=transport,
    )

    with pytest.raises(EmbeddingProviderError, match="exactly one embedding"):
        provider.embed("hello")


def test_ollama_embed_reports_malformed_vector_values() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        return FakeResponse({"embeddings": [[0.1, "bad"]]})

    provider = OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3-embedding:0.6b",
        transport=transport,
    )

    with pytest.raises(EmbeddingProviderError, match="non-numeric"):
        provider.embed("hello")
