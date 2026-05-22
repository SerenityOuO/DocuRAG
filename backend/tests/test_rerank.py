from __future__ import annotations

import pytest

from app.core.config import Settings
from app.schemas.rag import RetrievedChunk
from app.services.rerank import (
    FastEmbedRerankProvider,
    RerankProviderDisabledError,
    RerankProviderError,
    RerankService,
    create_rerank_provider,
)


def _candidate(chunk_id: str, text: str, score: float, metadata: dict[str, str] | None = None) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc-001",
        filename="invoice.txt",
        text=text,
        source="ocr_mock",
        created_at="2026-05-22T00:00:00Z",
        metadata=metadata or {},
        score=score,
    )


class StaticScoreProvider:
    name = "fastembed"
    model = "BAAI/bge-reranker-base"

    def __init__(self, scores: list[float]) -> None:
        self.scores = scores
        self.query = ""
        self.documents: list[str] = []

    def score(self, query: str, documents: list[str]) -> list[float]:
        self.query = query
        self.documents = documents
        return self.scores


class RaisingProvider:
    name = "fastembed"
    model = "BAAI/bge-reranker-base"

    def __init__(self, error: Exception) -> None:
        self.error = error

    def score(self, query: str, documents: list[str]) -> list[float]:
        raise self.error


def test_create_rerank_provider_returns_disabled_provider_without_env() -> None:
    provider = create_rerank_provider(Settings(rerank_provider=None))

    with pytest.raises(RerankProviderDisabledError, match="DOCURAG_RERANK_PROVIDER=fastembed"):
        provider.score("invoice total", ["invoice total amount"])


def test_rerank_service_sorts_limits_and_preserves_metadata() -> None:
    provider = StaticScoreProvider([0.2, 0.9, 0.4])
    service = RerankService(provider=provider, top_k=2, timeout_seconds=30, clock=lambda: 10.0)
    candidates = [
        _candidate("chunk-001", "generic invoice text", 0.12, {"vector_score": "0.120000"}),
        _candidate("chunk-002", "total amount is 1200", 0.99, {"vector_score": "0.990000"}),
        _candidate("chunk-003", "payment terms net 15", 0.55, {"vector_score": "0.550000"}),
    ]

    result = service.rerank("invoice total", candidates)

    assert provider.query == "invoice total"
    assert provider.documents == [
        "generic invoice text",
        "total amount is 1200",
        "payment terms net 15",
    ]
    assert result.status == "completed"
    assert result.input_candidate_count == 3
    assert result.output_candidate_count == 2
    assert [chunk.chunk_id for chunk in result.chunks] == ["chunk-002", "chunk-003"]
    assert result.chunks[0].score == 0.9
    assert result.chunks[0].metadata["vector_score"] == "0.990000"
    assert result.chunks[0].metadata["strategy_label"] == "vector_rerank"
    assert result.chunks[0].metadata["rerank_enabled"] == "true"
    assert result.chunks[0].metadata["rerank_provider"] == "fastembed"
    assert result.chunks[0].metadata["rerank_model"] == "BAAI/bge-reranker-base"
    assert result.chunks[0].metadata["rerank_input_rank"] == "2"
    assert result.chunks[0].metadata["rerank_rank"] == "1"
    assert result.chunks[0].metadata["rerank_score"] == "0.900000"
    assert result.chunks[0].metadata["pre_rerank_score"] == "0.990000"


def test_rerank_service_falls_back_when_provider_is_disabled() -> None:
    provider = create_rerank_provider(Settings(rerank_provider=""))
    service = RerankService(provider=provider, top_k=5, timeout_seconds=30)
    candidates = [_candidate("chunk-001", "invoice total", 0.5, {"vector_score": "0.500000"})]

    result = service.rerank("invoice total", candidates)

    assert result.status == "disabled"
    assert result.fallback_reason is not None
    assert result.chunks[0].chunk_id == "chunk-001"
    assert result.chunks[0].score == 0.5
    assert result.chunks[0].metadata["vector_score"] == "0.500000"
    assert result.chunks[0].metadata["rerank_enabled"] == "false"
    assert result.chunks[0].metadata["rerank_status"] == "disabled"
    assert "DOCURAG_RERANK_PROVIDER=fastembed" in result.chunks[0].metadata["rerank_fallback_reason"]


def test_rerank_service_falls_back_on_provider_error() -> None:
    provider = RaisingProvider(RerankProviderError("model unavailable"))
    service = RerankService(provider=provider, top_k=5, timeout_seconds=30)
    candidates = [_candidate("chunk-001", "invoice total", 0.5)]

    result = service.rerank("invoice total", candidates)

    assert result.status == "failed"
    assert result.fallback_reason == "model unavailable"
    assert result.chunks[0].chunk_id == "chunk-001"
    assert result.chunks[0].metadata["rerank_status"] == "failed"
    assert result.chunks[0].metadata["rerank_fallback_reason"] == "model unavailable"


def test_rerank_service_falls_back_on_timeout() -> None:
    provider = StaticScoreProvider([0.9])
    clock_values = iter([0.0, 31.0])
    service = RerankService(provider=provider, top_k=5, timeout_seconds=30, clock=lambda: next(clock_values))
    candidates = [_candidate("chunk-001", "invoice total", 0.5)]

    result = service.rerank("invoice total", candidates)

    assert result.status == "failed"
    assert result.fallback_reason is not None
    assert "timed out" in result.fallback_reason
    assert result.chunks[0].metadata["rerank_status"] == "failed"


def test_rerank_service_falls_back_on_malformed_score_count() -> None:
    provider = StaticScoreProvider([0.9])
    service = RerankService(provider=provider, top_k=5, timeout_seconds=30)
    candidates = [
        _candidate("chunk-001", "invoice total", 0.5),
        _candidate("chunk-002", "payment terms", 0.4),
    ]

    result = service.rerank("invoice total", candidates)

    assert result.status == "failed"
    assert result.fallback_reason == "Rerank provider returned 1 scores for 2 candidates."


def test_rerank_service_falls_back_on_non_numeric_score() -> None:
    provider = StaticScoreProvider([0.9, "bad"])  # type: ignore[list-item]
    service = RerankService(provider=provider, top_k=5, timeout_seconds=30)
    candidates = [
        _candidate("chunk-001", "invoice total", 0.5),
        _candidate("chunk-002", "payment terms", 0.4),
    ]

    result = service.rerank("invoice total", candidates)

    assert result.status == "failed"
    assert result.fallback_reason == "Rerank provider returned a non-numeric score."


def test_fastembed_provider_uses_encoder_rerank() -> None:
    class FakeEncoder:
        def rerank(self, query: str, documents: list[str]) -> list[float]:
            assert query == "invoice total"
            assert documents == ["a", "b"]
            return [0.1, 0.8]

    provider = FastEmbedRerankProvider(
        model="BAAI/bge-reranker-base",
        encoder_factory=lambda model: FakeEncoder(),
    )

    assert provider.score(" invoice total ", ["a", "b"]) == [0.1, 0.8]


def test_fastembed_provider_reports_unavailable_dependency() -> None:
    def missing_factory(model: str) -> object:
        raise ImportError("No module named fastembed")

    provider = FastEmbedRerankProvider(
        model="BAAI/bge-reranker-base",
        encoder_factory=missing_factory,
    )
    service = RerankService(provider=provider, top_k=5, timeout_seconds=30)
    candidates = [_candidate("chunk-001", "invoice total", 0.5)]

    result = service.rerank("invoice total", candidates)

    assert result.status == "failed"
    assert result.fallback_reason is not None
    assert "FastEmbed is not installed" in result.fallback_reason
