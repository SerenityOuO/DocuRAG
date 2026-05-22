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
class LlmGeneration:
    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_duration_ms: float | None = None
    load_duration_ms: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LlmHealth:
    provider: str
    enabled: bool
    available: bool
    message: str
    model: str | None = None
    base_url: str | None = None
    models: list[str] = field(default_factory=list)


class LlmProvider(Protocol):
    name: str

    def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
        pass

    def check_health(self) -> LlmHealth:
        pass


class LlmProviderError(RuntimeError):
    pass


class LlmProviderDisabledError(LlmProviderError):
    pass


class DisabledLlmProvider:
    name = "disabled"

    def __init__(self, reason: str = "Set DOCURAG_LLM_PROVIDER=ollama to enable local LLM generation.") -> None:
        self.reason = reason

    def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
        raise LlmProviderDisabledError(self.reason)

    def check_health(self) -> LlmHealth:
        return LlmHealth(
            provider=self.name,
            enabled=False,
            available=False,
            message=self.reason,
        )


class OllamaLlmProvider:
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

    def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise ValueError("prompt must not be empty")

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": cleaned_prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        data = self._request_json("POST", "/api/generate", payload)
        response_text = data.get("response")
        if not isinstance(response_text, str):
            raise LlmProviderError("Ollama response did not include a string 'response' field.")

        return LlmGeneration(
            text=response_text,
            model=str(data.get("model") or self.model),
            prompt_tokens=self._optional_int(data.get("prompt_eval_count")),
            completion_tokens=self._optional_int(data.get("eval_count")),
            total_duration_ms=self._nanoseconds_to_milliseconds(data.get("total_duration")),
            load_duration_ms=self._nanoseconds_to_milliseconds(data.get("load_duration")),
            raw=data,
        )

    def check_health(self) -> LlmHealth:
        try:
            data = self._request_json("GET", "/api/tags")
        except LlmProviderError as exc:
            return LlmHealth(
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
            return LlmHealth(
                provider=self.name,
                enabled=True,
                available=False,
                message=(
                    f"Ollama is reachable at {self.base_url}, but model '{self.model}' is not listed. "
                    f"Install or pull '{self.model}' before enabling LLM generation."
                ),
                model=self.model,
                base_url=self.base_url,
                models=model_names,
            )

        return LlmHealth(
            provider=self.name,
            enabled=True,
            available=True,
            message=f"Ollama model '{self.model}' is available.",
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
            raise LlmProviderError(f"Ollama request failed with HTTP {exc.code}: {message}") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise LlmProviderError(
                f"Ollama request timed out after {self.timeout_seconds:.1f}s at {self.base_url}."
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise LlmProviderError(
                    f"Ollama request timed out after {self.timeout_seconds:.1f}s at {self.base_url}."
                ) from exc
            raise LlmProviderError(
                f"Cannot connect to Ollama at {self.base_url}. Start Ollama and ensure model '{self.model}' is available."
            ) from exc

        try:
            data = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LlmProviderError("Ollama returned a non-JSON response.") from exc

        if not isinstance(data, dict):
            raise LlmProviderError("Ollama returned an unexpected JSON response shape.")

        return data

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


def create_llm_provider(settings: Settings) -> LlmProvider:
    provider_name = (settings.llm_provider or "").strip().lower()

    if not provider_name:
        return DisabledLlmProvider()

    if provider_name == "ollama":
        return OllamaLlmProvider(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    return DisabledLlmProvider(
        f"Unsupported DOCURAG_LLM_PROVIDER='{settings.llm_provider}'. Supported value for v0.10.0 is 'ollama'."
    )
