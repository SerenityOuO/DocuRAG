import json
import socket
from typing import Any
import urllib.error
import urllib.request

import pytest

from app.core.config import Settings
from app.services.llm import (
    LlmProviderDisabledError,
    LlmProviderError,
    OllamaLlmProvider,
    create_llm_provider,
)


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.closed = False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def close(self) -> None:
        self.closed = True


def test_create_llm_provider_returns_disabled_provider_without_env() -> None:
    provider = create_llm_provider(Settings(llm_provider=None))

    health = provider.check_health()

    assert health.enabled is False
    assert health.available is False
    with pytest.raises(LlmProviderDisabledError, match="DOCURAG_LLM_PROVIDER=ollama"):
        provider.generate("hello")


def test_ollama_generate_sends_non_streaming_request_and_parses_response() -> None:
    captured: dict[str, Any] = {}

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {
                "model": "qwen3.5:4b",
                "response": "Local answer",
                "prompt_eval_count": 7,
                "eval_count": 3,
                "total_duration": 12_000_000,
                "load_duration": 2_000_000,
                "done": True,
            }
        )

    provider = OllamaLlmProvider(
        base_url="http://127.0.0.1:11434/",
        model="qwen3.5:4b",
        timeout_seconds=5,
        transport=transport,
    )

    result = provider.generate("  hello  ", system="Only answer from context.")

    assert captured == {
        "url": "http://127.0.0.1:11434/api/generate",
        "method": "POST",
        "timeout": 5,
        "body": {
            "model": "qwen3.5:4b",
            "prompt": "hello",
            "stream": False,
            "system": "Only answer from context.",
        },
    }
    assert result.text == "Local answer"
    assert result.model == "qwen3.5:4b"
    assert result.prompt_tokens == 7
    assert result.completion_tokens == 3
    assert result.total_duration_ms == 12.0
    assert result.load_duration_ms == 2.0


def test_ollama_health_reports_model_available() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        assert request.full_url == "http://127.0.0.1:11434/api/tags"
        assert request.get_method() == "GET"
        return FakeResponse({"models": [{"name": "qwen3.5:4b"}]})

    provider = OllamaLlmProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:4b",
        transport=transport,
    )

    health = provider.check_health()

    assert health.enabled is True
    assert health.available is True
    assert health.models == ["qwen3.5:4b"]


def test_ollama_health_reports_missing_model() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        return FakeResponse({"models": [{"name": "llama3.2:3b"}]})

    provider = OllamaLlmProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:4b",
        transport=transport,
    )

    health = provider.check_health()

    assert health.enabled is True
    assert health.available is False
    assert "qwen3.5:4b" in health.message
    assert health.models == ["llama3.2:3b"]


def test_ollama_generate_reports_timeout() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        raise socket.timeout("timed out")

    provider = OllamaLlmProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:4b",
        timeout_seconds=1,
        transport=transport,
    )

    with pytest.raises(LlmProviderError, match="timed out after 1.0s"):
        provider.generate("hello")


def test_ollama_generate_reports_connection_error() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        raise urllib.error.URLError(ConnectionRefusedError("connection refused"))

    provider = OllamaLlmProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:4b",
        transport=transport,
    )

    with pytest.raises(LlmProviderError, match="Cannot connect to Ollama"):
        provider.generate("hello")


def test_ollama_generate_reports_http_error_body() -> None:
    error = urllib.error.HTTPError(
        url="http://127.0.0.1:11434/api/generate",
        code=404,
        msg="not found",
        hdrs=None,
        fp=FakeResponse({"error": "model 'qwen3.5:4b' not found"}),
    )

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        raise error

    provider = OllamaLlmProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:4b",
        transport=transport,
    )

    with pytest.raises(LlmProviderError, match="model 'qwen3.5:4b' not found"):
        provider.generate("hello")
