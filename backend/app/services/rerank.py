from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Protocol

from app.core.config import Settings
from app.schemas.rag import RetrievedChunk


ScoreClock = Callable[[], float]
EncoderFactory = Callable[[str], object]


@dataclass(frozen=True)
class RerankResult:
    chunks: list[RetrievedChunk]
    status: str
    provider: str
    model: str | None
    input_candidate_count: int
    output_candidate_count: int
    rerank_top_k: int
    latency_ms: float | None = None
    fallback_reason: str | None = None


class RerankProvider(Protocol):
    name: str
    model: str | None

    def score(self, query: str, documents: list[str]) -> list[float]:
        pass


class RerankProviderError(RuntimeError):
    pass


class RerankProviderDisabledError(RerankProviderError):
    pass


class RerankProviderUnavailableError(RerankProviderError):
    pass


class RerankProviderTimeoutError(RerankProviderError):
    pass


class DisabledRerankProvider:
    name = "disabled"
    model = None

    def __init__(
        self,
        reason: str = "Set DOCURAG_RERANK_PROVIDER=fastembed to enable optional reranking.",
    ) -> None:
        self.reason = reason

    def score(self, query: str, documents: list[str]) -> list[float]:
        raise RerankProviderDisabledError(self.reason)


class FastEmbedRerankProvider:
    name = "fastembed"

    def __init__(
        self,
        model: str,
        encoder_factory: EncoderFactory | None = None,
    ) -> None:
        self.model = model
        self._encoder_factory = encoder_factory or self._default_encoder_factory
        self._encoder: object | None = None

    def score(self, query: str, documents: list[str]) -> list[float]:
        cleaned_query = query.strip()
        if not cleaned_query:
            raise ValueError("query must not be empty")
        if not documents:
            return []

        encoder = self._get_encoder()
        rerank = getattr(encoder, "rerank", None)
        if not callable(rerank):
            raise RerankProviderError("FastEmbed reranker does not expose a callable rerank method.")

        try:
            scores = list(rerank(cleaned_query, documents))
        except RerankProviderError:
            raise
        except Exception as exc:
            raise RerankProviderError(f"FastEmbed rerank failed: {exc}") from exc

        return scores

    def _get_encoder(self) -> object:
        if self._encoder is None:
            try:
                self._encoder = self._encoder_factory(self.model)
            except ImportError as exc:
                raise RerankProviderUnavailableError(
                    "FastEmbed is not installed. Install the optional rerank dependency before enabling DOCURAG_RERANK_PROVIDER=fastembed."
                ) from exc
            except Exception as exc:
                raise RerankProviderUnavailableError(f"FastEmbed reranker could not be initialized: {exc}") from exc

        return self._encoder

    def _default_encoder_factory(self, model: str) -> object:
        from fastembed.rerank.cross_encoder import TextCrossEncoder

        return TextCrossEncoder(model_name=model)


class RerankService:
    def __init__(
        self,
        provider: RerankProvider,
        top_k: int,
        timeout_seconds: float,
        clock: ScoreClock = perf_counter,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        self.provider = provider
        self.top_k = top_k
        self.timeout_seconds = timeout_seconds
        self._clock = clock

    def rerank(self, query: str, candidates: list[RetrievedChunk]) -> RerankResult:
        if not candidates:
            return RerankResult(
                chunks=[],
                status="completed",
                provider=self.provider.name,
                model=self.provider.model,
                input_candidate_count=0,
                output_candidate_count=0,
                rerank_top_k=self.top_k,
                latency_ms=0.0,
            )

        started_at = self._clock()
        try:
            scores = self.provider.score(query, [candidate.text for candidate in candidates])
            latency_ms = (self._clock() - started_at) * 1000
            if latency_ms > self.timeout_seconds * 1000:
                raise RerankProviderTimeoutError(
                    f"Rerank provider '{self.provider.name}' timed out after {self.timeout_seconds:.1f}s."
                )
            self._validate_scores(scores, candidates)
        except RerankProviderDisabledError as exc:
            return self._fallback(candidates, "disabled", str(exc))
        except RerankProviderError as exc:
            return self._fallback(candidates, "failed", str(exc))

        ranked = sorted(
            enumerate(zip(candidates, scores, strict=True)),
            key=lambda item: (-float(item[1][1]), item[0]),
        )
        selected = ranked[: min(self.top_k, len(ranked))]
        reranked_chunks = [
            self._with_success_metadata(
                chunk=chunk,
                score=float(score),
                input_rank=index + 1,
                rerank_rank=rank + 1,
                input_candidate_count=len(candidates),
                latency_ms=latency_ms,
            )
            for rank, (index, (chunk, score)) in enumerate(selected)
        ]

        return RerankResult(
            chunks=reranked_chunks,
            status="completed",
            provider=self.provider.name,
            model=self.provider.model,
            input_candidate_count=len(candidates),
            output_candidate_count=len(reranked_chunks),
            rerank_top_k=self.top_k,
            latency_ms=latency_ms,
        )

    def _validate_scores(self, scores: list[float], candidates: list[RetrievedChunk]) -> None:
        if len(scores) != len(candidates):
            raise RerankProviderError(
                f"Rerank provider returned {len(scores)} scores for {len(candidates)} candidates."
            )

        for score in scores:
            if not isinstance(score, (int, float)):
                raise RerankProviderError("Rerank provider returned a non-numeric score.")

    def _fallback(self, candidates: list[RetrievedChunk], status: str, reason: str) -> RerankResult:
        fallback_chunks = [
            chunk.model_copy(
                update={
                    "metadata": {
                        **chunk.metadata,
                        "rerank_enabled": "false",
                        "rerank_status": status,
                        "rerank_provider": self.provider.name,
                        "rerank_model": str(self.provider.model or ""),
                        "rerank_fallback_reason": reason[:500],
                    }
                }
            )
            for chunk in candidates
        ]

        return RerankResult(
            chunks=fallback_chunks,
            status=status,
            provider=self.provider.name,
            model=self.provider.model,
            input_candidate_count=len(candidates),
            output_candidate_count=len(fallback_chunks),
            rerank_top_k=self.top_k,
            fallback_reason=reason[:500],
        )

    def _with_success_metadata(
        self,
        chunk: RetrievedChunk,
        score: float,
        input_rank: int,
        rerank_rank: int,
        input_candidate_count: int,
        latency_ms: float,
    ) -> RetrievedChunk:
        return chunk.model_copy(
            update={
                "score": score,
                "metadata": {
                    **chunk.metadata,
                    "strategy_label": "vector_rerank",
                    "rerank_enabled": "true",
                    "rerank_status": "completed",
                    "rerank_provider": self.provider.name,
                    "rerank_model": str(self.provider.model or ""),
                    "rerank_input_candidate_count": str(input_candidate_count),
                    "rerank_top_k": str(self.top_k),
                    "rerank_input_rank": str(input_rank),
                    "rerank_rank": str(rerank_rank),
                    "rerank_score": f"{score:.6f}",
                    "rerank_latency_ms": f"{latency_ms:.2f}",
                    "pre_rerank_score": f"{chunk.score:.6f}",
                },
            }
        )


def create_rerank_provider(settings: Settings) -> RerankProvider:
    provider_name = (settings.rerank_provider or "").strip().lower()

    if not provider_name or provider_name == "disabled":
        return DisabledRerankProvider()

    if provider_name == "fastembed":
        return FastEmbedRerankProvider(model=settings.rerank_model)

    return DisabledRerankProvider(
        f"Unsupported DOCURAG_RERANK_PROVIDER='{settings.rerank_provider}'. Supported value for v0.15.0 is 'fastembed'."
    )


def create_rerank_service(settings: Settings, provider: RerankProvider | None = None) -> RerankService:
    return RerankService(
        provider=provider or create_rerank_provider(settings),
        top_k=settings.rerank_top_k,
        timeout_seconds=settings.rerank_timeout_seconds,
    )
