from __future__ import annotations

from dataclasses import dataclass, field
import json
import socket
from time import perf_counter
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
    total_tokens: int | None = None
    finish_reason: str | None = None
    provider_latency_ms: float | None = None
    tokens_per_second: float | None = None
    provider_request_id: str | None = None
    total_duration_ms: float | None = None
    load_duration_ms: float | None = None
    think: bool | None = None
    num_predict: int | None = None
    timeout_ms: int | None = None
    streaming_mode: str = "disabled"
    truncated_reason: str | None = None
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
        think: bool = False,
        num_predict: int | None = 512,
        transport: Transport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.think = think
        self.num_predict = num_predict if num_predict is None or num_predict > 0 else None
        self._transport = transport or (lambda request, timeout: urllib.request.urlopen(request, timeout=timeout))

    def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise ValueError("prompt must not be empty")

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": cleaned_prompt,
            "stream": False,
            "think": self.think,
        }
        if self.num_predict is not None:
            payload["options"] = {"num_predict": self.num_predict}
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
            think=self.think,
            num_predict=self.num_predict,
            timeout_ms=self._timeout_milliseconds(),
            streaming_mode="disabled",
            truncated_reason=self._truncated_reason(data),
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

    def _timeout_milliseconds(self) -> int:
        return int(self.timeout_seconds * 1000)

    def _truncated_reason(self, data: dict[str, Any]) -> str | None:
        done_reason = data.get("done_reason")
        if isinstance(done_reason, str) and done_reason.lower() in {"length", "max_tokens", "num_predict"}:
            return done_reason
        if data.get("done") is False:
            return "provider_not_done"
        return None


class OpenAiCompatibleLlmProvider:
    name = "openai_compatible"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 30.0,
        api_key: str | None = None,
        max_tokens: int | None = 512,
        transport: Transport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.api_key = api_key.strip() if api_key and api_key.strip() else None
        self.max_tokens = max_tokens if max_tokens is None or max_tokens > 0 else None
        self._transport = transport or (lambda request, timeout: urllib.request.urlopen(request, timeout=timeout))

    def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise ValueError("prompt must not be empty")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": cleaned_prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens

        started_at = perf_counter()
        data = self._request_json("POST", "/chat/completions", payload)
        latency_ms = (perf_counter() - started_at) * 1000

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise LlmProviderError("OpenAI-compatible response did not include a choices array.")

        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise LlmProviderError("OpenAI-compatible response did not include choices[0].message.")

        response_text = message.get("content")
        if not isinstance(response_text, str):
            raise LlmProviderError("OpenAI-compatible response did not include a string message content.")

        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        completion_tokens = self._optional_int(usage.get("completion_tokens"))

        return LlmGeneration(
            text=response_text,
            model=str(data.get("model") or self.model),
            prompt_tokens=self._optional_int(usage.get("prompt_tokens")),
            completion_tokens=completion_tokens,
            total_tokens=self._optional_int(usage.get("total_tokens")),
            finish_reason=str(choices[0].get("finish_reason")) if choices[0].get("finish_reason") else None,
            provider_latency_ms=latency_ms,
            tokens_per_second=self._tokens_per_second(completion_tokens, latency_ms),
            provider_request_id=str(data.get("id")) if data.get("id") else None,
            num_predict=self.max_tokens,
            timeout_ms=self._timeout_milliseconds(),
            streaming_mode="disabled",
            truncated_reason="max_tokens" if choices[0].get("finish_reason") == "length" else None,
            raw=data,
        )

    def check_health(self) -> LlmHealth:
        try:
            data = self._request_json("GET", "/models")
        except LlmProviderError as exc:
            return LlmHealth(
                provider=self.name,
                enabled=True,
                available=False,
                message=str(exc),
                model=self.model,
                base_url=self.base_url,
            )

        raw_models = data.get("data")
        model_names = [
            str(item.get("id"))
            for item in raw_models or []
            if isinstance(item, dict) and item.get("id")
        ]

        if model_names and self.model not in model_names:
            return LlmHealth(
                provider=self.name,
                enabled=True,
                available=False,
                message=(
                    f"OpenAI-compatible endpoint is reachable at {self.base_url}, but model "
                    f"'{self.model}' is not listed."
                ),
                model=self.model,
                base_url=self.base_url,
                models=model_names,
            )

        return LlmHealth(
            provider=self.name,
            enabled=True,
            available=True,
            message=f"OpenAI-compatible endpoint is reachable for model '{self.model}'.",
            model=self.model,
            base_url=self.base_url,
            models=model_names,
        )

    def _request_json(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers=headers,
        )

        try:
            response = self._transport(request, self.timeout_seconds)
            try:
                response_body = response.read()
            finally:
                response.close()
        except urllib.error.HTTPError as exc:
            message = self._read_http_error(exc)
            raise LlmProviderError(f"OpenAI-compatible request failed with HTTP {exc.code}: {message}") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise LlmProviderError(
                f"OpenAI-compatible request timed out after {self.timeout_seconds:.1f}s at {self.base_url}."
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise LlmProviderError(
                    f"OpenAI-compatible request timed out after {self.timeout_seconds:.1f}s at {self.base_url}."
                ) from exc
            raise LlmProviderError(
                f"Cannot connect to OpenAI-compatible endpoint at {self.base_url}."
            ) from exc

        try:
            data = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LlmProviderError("OpenAI-compatible endpoint returned a non-JSON response.") from exc

        if not isinstance(data, dict):
            raise LlmProviderError("OpenAI-compatible endpoint returned an unexpected JSON response shape.")

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
            error = data.get("error")
            if isinstance(error, dict):
                message = error.get("message")
                if message:
                    return str(message)
            message = data.get("message")
            if message:
                return str(message)

        return error_body or "unknown error"

    def _optional_int(self, value: object) -> int | None:
        if isinstance(value, int):
            return value
        return None

    def _tokens_per_second(self, completion_tokens: int | None, latency_ms: float) -> float | None:
        if completion_tokens is None or latency_ms <= 0:
            return None
        return completion_tokens / (latency_ms / 1000)

    def _timeout_milliseconds(self) -> int:
        return int(self.timeout_seconds * 1000)


def create_llm_provider(settings: Settings) -> LlmProvider:
    provider_name = (settings.llm_provider or "").strip().lower()

    if not provider_name:
        return DisabledLlmProvider()

    if provider_name == "ollama":
        return OllamaLlmProvider(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            think=settings.llm_think,
            num_predict=settings.llm_num_predict,
        )

    if provider_name == "openai_compatible":
        return OpenAiCompatibleLlmProvider(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            api_key=settings.llm_api_key,
            max_tokens=settings.llm_num_predict,
        )

    return DisabledLlmProvider(
        f"Unsupported DOCURAG_LLM_PROVIDER='{settings.llm_provider}'. Supported values are 'ollama' and 'openai_compatible'."
    )
