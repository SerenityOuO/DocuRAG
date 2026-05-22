from __future__ import annotations

from dataclasses import dataclass, field
import json
import socket
from typing import Any, Callable, Protocol
import urllib.error
import urllib.request

from app.core.config import Settings


Transport = Callable[[urllib.request.Request, float], Any]


@dataclass(frozen=True)
class EmbeddingResult:
    embedding: list[float]
    model: str
    total_duration_ms: float | None = None
    load_duration_ms: float | None = None
    prompt_tokens: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def dimension(self) -> int:
        return len(self.embedding)


@dataclass(frozen=True)
class EmbeddingHealth:
    provider: str
    enabled: bool
    available: bool
    message: str
    model: str | None = None
    base_url: str | None = None
    models: list[str] = field(default_factory=list)


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, text: str) -> EmbeddingResult:
        pass

    def check_health(self) -> EmbeddingHealth:
        pass


class EmbeddingProviderError(RuntimeError):
    pass


class EmbeddingProviderDisabledError(EmbeddingProviderError):
    pass


class DisabledEmbeddingProvider:
    name = "disabled"

    def __init__(
        self,
        reason: str = "Set DOCURAG_EMBEDDING_PROVIDER=ollama to enable local embeddings.",
    ) -> None:
        self.reason = reason

    def embed(self, text: str) -> EmbeddingResult:
        raise EmbeddingProviderDisabledError(self.reason)

    def check_health(self) -> EmbeddingHealth:
        return EmbeddingHealth(
            provider=self.name,
            enabled=False,
            available=False,
            message=self.reason,
        )


class OllamaEmbeddingProvider:
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 30.0,
        transport: Transport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._transport = transport or (lambda request, timeout: urllib.request.urlopen(request, timeout=timeout))

    def embed(self, text: str) -> EmbeddingResult:
        cleaned_text = text.strip()
        if not cleaned_text:
            raise ValueError("text must not be empty")

        data = self._request_json("POST", "/api/embed", {"model": self.model, "input": cleaned_text})
        embedding = self._extract_single_embedding(data)

        return EmbeddingResult(
            embedding=embedding,
            model=str(data.get("model") or self.model),
            total_duration_ms=self._nanoseconds_to_milliseconds(data.get("total_duration")),
            load_duration_ms=self._nanoseconds_to_milliseconds(data.get("load_duration")),
            prompt_tokens=self._optional_int(data.get("prompt_eval_count")),
            raw=data,
        )

    def check_health(self) -> EmbeddingHealth:
        try:
            data = self._request_json("GET", "/api/tags")
        except EmbeddingProviderError as exc:
            return EmbeddingHealth(
                provider=self.name,
                enabled=True,
                available=False,
                message=str(exc),
                model=self.model,
                base_url=self.base_url,
            )

        models = data.get("models")
        model_names = [
            str(item.get("name"))
            for item in models or []
            if isinstance(item, dict) and item.get("name")
        ]

        if self.model not in model_names:
            return EmbeddingHealth(
                provider=self.name,
                enabled=True,
                available=False,
                message=(
                    f"Ollama is reachable at {self.base_url}, but embedding model '{self.model}' is not listed. "
                    f"Install or pull '{self.model}' before enabling vector retrieval."
                ),
                model=self.model,
                base_url=self.base_url,
                models=model_names,
            )

        return EmbeddingHealth(
            provider=self.name,
            enabled=True,
            available=True,
            message=f"Ollama embedding model '{self.model}' is available.",
            model=self.model,
            base_url=self.base_url,
            models=model_names,
        )

    def _request_json(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        try:
            response = self._transport(request, self.timeout_seconds)
            try:
                response_body = response.read()
            finally:
                response.close()
        except urllib.error.HTTPError as exc:
            message = self._read_http_error(exc)
            raise EmbeddingProviderError(f"Ollama embedding request failed with HTTP {exc.code}: {message}") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise EmbeddingProviderError(
                f"Ollama embedding request timed out after {self.timeout_seconds:.1f}s at {self.base_url}."
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise EmbeddingProviderError(
                    f"Ollama embedding request timed out after {self.timeout_seconds:.1f}s at {self.base_url}."
                ) from exc
            raise EmbeddingProviderError(
                f"Cannot connect to Ollama at {self.base_url}. Start Ollama and ensure embedding model '{self.model}' is available."
            ) from exc

        try:
            data = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EmbeddingProviderError("Ollama embedding API returned a non-JSON response.") from exc

        if not isinstance(data, dict):
            raise EmbeddingProviderError("Ollama embedding API returned an unexpected JSON response shape.")

        return data

    def _extract_single_embedding(self, data: dict[str, Any]) -> list[float]:
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != 1:
            raise EmbeddingProviderError("Ollama embedding response did not include exactly one embedding.")

        embedding = embeddings[0]
        if not isinstance(embedding, list) or not embedding:
            raise EmbeddingProviderError("Ollama embedding response included an empty or malformed embedding.")

        vector: list[float] = []
        for value in embedding:
            if not isinstance(value, (int, float)):
                raise EmbeddingProviderError("Ollama embedding response included a non-numeric vector value.")
            vector.append(float(value))

        return vector

    def _read_http_error(self, exc: urllib.error.HTTPError) -> str:
        try:
            error_body = exc.read().decode("utf-8")
        except Exception:
            return exc.reason or "unknown error"

        try:
            data = json.loads(error_body)
        except json.JSONDecodeError:
            return error_body or "unknown error"

        if isinstance(data, dict):
            message = data.get("error") or data.get("message")
            if message:
                return str(message)

        return error_body or "unknown error"

    def _optional_int(self, value: object) -> int | None:
        if isinstance(value, int):
            return value
        return None

    def _nanoseconds_to_milliseconds(self, value: object) -> float | None:
        if not isinstance(value, int):
            return None
        return value / 1_000_000


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider_name = (settings.embedding_provider or "").strip().lower()

    if not provider_name:
        return DisabledEmbeddingProvider()

    if provider_name == "ollama":
        return OllamaEmbeddingProvider(
            base_url=settings.embedding_base_url,
            model=settings.embedding_model,
            timeout_seconds=settings.embedding_timeout_seconds,
        )

    return DisabledEmbeddingProvider(
        f"Unsupported DOCURAG_EMBEDDING_PROVIDER='{settings.embedding_provider}'. Supported value for v0.11.0 is 'ollama'."
    )
