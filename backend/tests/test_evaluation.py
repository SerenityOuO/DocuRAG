from app.schemas.rag import RagQueryResponse, RetrievedChunk
from app.services.evaluation import (
    HybridEvalProvider,
    HybridRerankEvalProvider,
    RetrievalEvalCase,
    VectorRerankEvalProvider,
    evaluate_retrieval_response,
    summarize_results,
)
from app.services.rag import KeywordRagProvider
from app.services.rerank import RerankProviderError, RerankService


def make_case() -> RetrievalEvalCase:
    return RetrievalEvalCase(
        id="invoice_payment_terms",
        query="What are the payment terms?",
        top_k=3,
        expected_document_filenames=["mock-invoice-aurora.txt"],
        expected_chunk_hints=["Payment terms: Net 15", "Amount due: USD 1,248.50"],
        expected_terms=["Net 15", "USD 1,248.50"],
        tags=["invoice", "payment"],
    )


def make_chunk(
    text: str,
    chunk_id: str = "chunk-001",
    filename: str = "mock-invoice-aurora.txt",
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc-001",
        filename=filename,
        text=text,
        source="eval_fixture",
        created_at="2026-05-22T00:00:00Z",
        source_type="eval_fixture",
        metadata=metadata or {},
        score=1.0,
    )


def make_response(chunks: list[RetrievedChunk]) -> RagQueryResponse:
    return RagQueryResponse(answer="answer", citations=[], retrieved_chunks=chunks)


class StaticRerankProvider:
    name = "fastembed"
    model = "BAAI/bge-reranker-base"

    def __init__(self, scores: list[float]) -> None:
        self.scores = scores
        self.documents: list[str] = []

    def score(self, query: str, documents: list[str]) -> list[float]:
        self.documents = documents
        return self.scores


class RaisingRerankProvider:
    name = "fastembed"
    model = "BAAI/bge-reranker-base"

    def score(self, query: str, documents: list[str]) -> list[float]:
        raise RerankProviderError("reranker unavailable")


class StubVectorProvider:
    name = "vector"

    def __init__(self, response: RagQueryResponse) -> None:
        self.response = response

    def query(self, query: str, top_k: int, documents: list[object]) -> RagQueryResponse:
        return self.response


class StubKeywordProvider(KeywordRagProvider):
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        super().__init__()
        self.chunks = chunks

    def retrieve(self, query: str, top_k: int, documents: list[object]) -> list[RetrievedChunk]:
        return self.chunks[:top_k]


def test_evaluate_retrieval_response_calculates_hit_mrr_and_recall() -> None:
    case = make_case()
    response = make_response(
        [
            make_chunk("Line items include monitor arms.", "chunk-001"),
            make_chunk("Payment terms: Net 15", "chunk-002"),
            make_chunk("Amount due: USD 1,248.50", "chunk-003"),
        ]
    )

    result = evaluate_retrieval_response(case, response, "keyword", latency_ms=12.345)

    assert result.hit is True
    assert result.first_relevant_rank == 2
    assert result.reciprocal_rank == 0.5
    assert result.recall_at_k == 1.0
    assert result.matched_expected_terms == ["Net 15", "USD 1,248.50"]
    assert result.to_dict()["latency_ms"] == 12.35


def test_evaluate_retrieval_response_requires_expected_evidence() -> None:
    case = make_case()
    response = make_response(
        [
            make_chunk("Invoice number: AUR-2026-051", "chunk-001"),
        ]
    )

    result = evaluate_retrieval_response(case, response, "keyword", latency_ms=1.0)

    assert result.hit is False
    assert result.first_relevant_rank is None
    assert result.reciprocal_rank == 0.0
    assert result.recall_at_k == 0.0
    assert result.matched_expected_terms == []


def test_evaluate_retrieval_response_handles_empty_retrieval() -> None:
    result = evaluate_retrieval_response(make_case(), make_response([]), "keyword", latency_ms=1.0)

    assert result.hit is False
    assert result.first_relevant_rank is None
    assert result.retrieved_chunks == []
    assert result.recall_at_k == 0.0


def test_evaluate_retrieval_response_marks_vector_unavailable_fallback() -> None:
    response = make_response(
        [
            make_chunk(
                "Payment terms: Net 15",
                metadata={
                    "vector_retrieval_status": "failed",
                    "vector_retrieval_error": "Cannot connect to Qdrant",
                },
            )
        ]
    )

    result = evaluate_retrieval_response(make_case(), response, "vector", latency_ms=1.0)

    assert result.strategy == "vector_unavailable_fallback"
    assert result.error == "Cannot connect to Qdrant"
    assert result.hit is True


def test_evaluate_retrieval_response_marks_vector_rerank_vector_fallback() -> None:
    response = make_response(
        [
            make_chunk(
                "Payment terms: Net 15",
                metadata={
                    "vector_retrieval_status": "failed",
                    "vector_retrieval_error": "Cannot connect to Qdrant",
                },
            )
        ]
    )

    result = evaluate_retrieval_response(make_case(), response, "vector_rerank", latency_ms=1.0)

    assert result.strategy == "vector_unavailable_fallback"
    assert result.error == "Cannot connect to Qdrant"
    assert result.hit is True


def test_evaluate_retrieval_response_does_not_count_hybrid_vector_fallback_as_failure() -> None:
    response = make_response(
        [
            make_chunk(
                "Payment terms: Net 15",
                metadata={
                    "strategy_label": "hybrid",
                    "vector_retrieval_status": "failed",
                    "vector_retrieval_error": "Cannot connect to Qdrant",
                },
            )
        ]
    )

    result = evaluate_retrieval_response(make_case(), response, "hybrid", latency_ms=1.0)

    assert result.strategy == "hybrid"
    assert result.error is None
    assert result.hit is True


def test_evaluate_retrieval_response_does_not_count_hybrid_rerank_vector_fallback_as_failure() -> None:
    response = make_response(
        [
            make_chunk(
                "Payment terms: Net 15",
                metadata={
                    "strategy_label": "hybrid_rerank",
                    "vector_retrieval_status": "failed",
                    "vector_retrieval_error": "Cannot connect to Qdrant",
                },
            )
        ]
    )

    result = evaluate_retrieval_response(make_case(), response, "hybrid_rerank", latency_ms=1.0)

    assert result.strategy == "hybrid_rerank"
    assert result.error is None
    assert result.hit is True


def test_hybrid_eval_provider_merges_and_dedupes_keyword_and_vector_candidates() -> None:
    provider = HybridEvalProvider(
        keyword_provider=StubKeywordProvider(
            [
                make_chunk("Payment terms: Net 15", "chunk-001", metadata={"keyword_marker": "yes"}),
                make_chunk("Amount due: USD 1,248.50", "chunk-002"),
            ]
        ),
        vector_provider=StubVectorProvider(
            make_response(
                [
                    make_chunk("Payment terms: Net 15", "chunk-001", metadata={"vector_score": "0.900000"}),
                    make_chunk("Line items include monitor arms.", "chunk-003", metadata={"vector_score": "0.500000"}),
                ]
            )
        ),
    )

    response = provider.query("payment terms", 3, [])

    assert [chunk.chunk_id for chunk in response.retrieved_chunks] == ["chunk-001", "chunk-002", "chunk-003"]
    first_metadata = response.retrieved_chunks[0].metadata
    assert first_metadata["strategy_label"] == "hybrid"
    assert first_metadata["merge_policy"] == "rank_based_fusion"
    assert first_metadata["branches"] == "keyword,vector"
    assert first_metadata["keyword_rank"] == "1"
    assert first_metadata["vector_rank"] == "1"
    assert first_metadata["keyword_candidate_count"] == "2"
    assert first_metadata["vector_candidate_count"] == "2"
    assert first_metadata["merged_candidate_count"] == "3"
    assert first_metadata["deduped_candidate_count"] == "1"
    assert response.citations[0].trace_metadata["strategy_label"] == "hybrid"


def test_hybrid_eval_provider_falls_back_to_keyword_when_vector_branch_fails() -> None:
    provider = HybridEvalProvider(
        keyword_provider=StubKeywordProvider([make_chunk("Payment terms: Net 15", "chunk-001")]),
        vector_provider=StubVectorProvider(
            make_response(
                [
                    make_chunk(
                        "Payment terms: Net 15",
                        "chunk-001",
                        metadata={
                            "vector_retrieval_status": "failed",
                            "vector_retrieval_error": "Qdrant unavailable",
                        },
                    )
                ]
            )
        ),
    )

    response = provider.query("payment terms", 3, [])

    assert [chunk.chunk_id for chunk in response.retrieved_chunks] == ["chunk-001"]
    metadata = response.retrieved_chunks[0].metadata
    assert metadata["strategy_label"] == "hybrid"
    assert metadata["branches"] == "keyword"
    assert metadata["branch_failures"] == "vector"
    assert metadata["fallback_reason"] == "Qdrant unavailable"
    assert response.citations[0].trace_metadata["fallback_reason"] == "Qdrant unavailable"


def test_hybrid_rerank_eval_provider_reranks_hybrid_candidates() -> None:
    rerank_provider = StaticRerankProvider([0.1, 0.9, 0.2])
    hybrid_provider = HybridEvalProvider(
        keyword_provider=StubKeywordProvider(
            [
                make_chunk("Payment terms: Net 15", "chunk-001"),
                make_chunk("Amount due: USD 1,248.50", "chunk-002"),
            ]
        ),
        vector_provider=StubVectorProvider(
            make_response(
                [
                    make_chunk("Payment terms: Net 15", "chunk-001", metadata={"vector_score": "0.900000"}),
                    make_chunk("Line items include monitor arms.", "chunk-003", metadata={"vector_score": "0.500000"}),
                ]
            )
        ),
    )
    provider = HybridRerankEvalProvider(
        hybrid_provider=hybrid_provider,
        response_builder=KeywordRagProvider(),
        rerank_service=RerankService(provider=rerank_provider, top_k=3, timeout_seconds=30),
    )

    response = provider.query("amount due", 3, [])

    assert rerank_provider.documents == [
        "Payment terms: Net 15",
        "Amount due: USD 1,248.50",
        "Line items include monitor arms.",
    ]
    assert [chunk.chunk_id for chunk in response.retrieved_chunks] == ["chunk-002", "chunk-003", "chunk-001"]
    metadata = response.retrieved_chunks[0].metadata
    assert metadata["strategy_label"] == "hybrid_rerank"
    assert metadata["candidate_flow"] == "keyword+vector -> hybrid_merge -> rerank"
    assert metadata["rerank_enabled"] == "true"
    assert metadata["rerank_status"] == "completed"
    assert metadata["rerank_score"] == "0.900000"
    assert metadata["rerank_rank"] == "1"
    assert metadata["merged_score"] == "0.016129"
    assert metadata["hybrid_candidate_count"] == "3"
    assert metadata["rerank_input_count"] == "3"
    assert metadata["fallback_state"] == "none"
    assert response.citations[0].trace_metadata["strategy_label"] == "hybrid_rerank"


def test_hybrid_rerank_eval_provider_preserves_hybrid_candidates_on_rerank_failure() -> None:
    provider = HybridRerankEvalProvider(
        hybrid_provider=HybridEvalProvider(
            keyword_provider=StubKeywordProvider(
                [
                    make_chunk("Payment terms: Net 15", "chunk-001"),
                    make_chunk("Amount due: USD 1,248.50", "chunk-002"),
                ]
            ),
            vector_provider=StubVectorProvider(make_response([])),
        ),
        response_builder=KeywordRagProvider(),
        rerank_service=RerankService(provider=RaisingRerankProvider(), top_k=2, timeout_seconds=30),
    )

    response = provider.query("amount due", 2, [])

    assert [chunk.chunk_id for chunk in response.retrieved_chunks] == ["chunk-001", "chunk-002"]
    metadata = response.retrieved_chunks[0].metadata
    assert metadata["strategy_label"] == "hybrid_rerank"
    assert metadata["rerank_enabled"] == "false"
    assert metadata["rerank_status"] == "failed"
    assert metadata["rerank_fallback_reason"] == "reranker unavailable"
    assert metadata["merge_policy"] == "rank_based_fusion"
    assert metadata["fallback_state"] == "reranker_unavailable"


def test_hybrid_rerank_eval_provider_keeps_vector_branch_fallback_metadata() -> None:
    rerank_provider = StaticRerankProvider([0.9])
    provider = HybridRerankEvalProvider(
        hybrid_provider=HybridEvalProvider(
            keyword_provider=StubKeywordProvider([make_chunk("Payment terms: Net 15", "chunk-001")]),
            vector_provider=StubVectorProvider(
                make_response(
                    [
                        make_chunk(
                            "Payment terms: Net 15",
                            "chunk-001",
                            metadata={
                                "vector_retrieval_status": "failed",
                                "vector_retrieval_error": "Qdrant unavailable",
                            },
                        )
                    ]
                )
            ),
        ),
        response_builder=KeywordRagProvider(),
        rerank_service=RerankService(provider=rerank_provider, top_k=2, timeout_seconds=30),
    )

    response = provider.query("payment terms", 2, [])

    assert [chunk.chunk_id for chunk in response.retrieved_chunks] == ["chunk-001"]
    metadata = response.retrieved_chunks[0].metadata
    assert metadata["strategy_label"] == "hybrid_rerank"
    assert metadata["branch_failures"] == "vector"
    assert metadata["fallback_reason"] == "Qdrant unavailable"
    assert metadata["vector_retrieval_status"] == "failed"
    assert metadata["rerank_status"] == "completed"
    assert metadata["fallback_state"] == "vector_unavailable"


def test_vector_rerank_eval_provider_reranks_vector_candidates() -> None:
    rerank_provider = StaticRerankProvider([0.1, 0.9])
    provider = VectorRerankEvalProvider(
        vector_provider=StubVectorProvider(
            make_response(
                [
                    make_chunk("Payment terms: Net 15", "chunk-001", metadata={"vector_score": "0.500000"}),
                    make_chunk("Amount due: USD 1,248.50", "chunk-002", metadata={"vector_score": "0.400000"}),
                ]
            )
        ),
        response_builder=KeywordRagProvider(),
        rerank_service=RerankService(provider=rerank_provider, top_k=2, timeout_seconds=30),
    )

    response = provider.query("amount due", 2, [])

    assert rerank_provider.documents == ["Payment terms: Net 15", "Amount due: USD 1,248.50"]
    assert [chunk.chunk_id for chunk in response.retrieved_chunks] == ["chunk-002", "chunk-001"]
    assert response.retrieved_chunks[0].metadata["strategy_label"] == "vector_rerank"
    assert response.retrieved_chunks[0].metadata["rerank_enabled"] == "true"
    assert response.retrieved_chunks[0].metadata["rerank_score"] == "0.900000"
    assert response.citations[0].trace_metadata["strategy_label"] == "vector_rerank"


def test_vector_rerank_eval_provider_preserves_candidates_on_rerank_failure() -> None:
    provider = VectorRerankEvalProvider(
        vector_provider=StubVectorProvider(
            make_response(
                [
                    make_chunk("Payment terms: Net 15", "chunk-001", metadata={"vector_score": "0.500000"}),
                    make_chunk("Amount due: USD 1,248.50", "chunk-002", metadata={"vector_score": "0.400000"}),
                ]
            )
        ),
        response_builder=KeywordRagProvider(),
        rerank_service=RerankService(provider=RaisingRerankProvider(), top_k=2, timeout_seconds=30),
    )

    response = provider.query("amount due", 2, [])

    assert [chunk.chunk_id for chunk in response.retrieved_chunks] == ["chunk-001", "chunk-002"]
    assert response.retrieved_chunks[0].metadata["rerank_enabled"] == "false"
    assert response.retrieved_chunks[0].metadata["rerank_status"] == "failed"
    assert response.retrieved_chunks[0].metadata["rerank_fallback_reason"] == "reranker unavailable"


def test_vector_rerank_eval_provider_skips_rerank_when_vector_falls_back() -> None:
    rerank_provider = StaticRerankProvider([0.9])
    provider = VectorRerankEvalProvider(
        vector_provider=StubVectorProvider(
            make_response(
                [
                    make_chunk(
                        "Payment terms: Net 15",
                        "chunk-001",
                        metadata={
                            "vector_retrieval_status": "failed",
                            "vector_retrieval_error": "Qdrant unavailable",
                        },
                    )
                ]
            )
        ),
        response_builder=KeywordRagProvider(),
        rerank_service=RerankService(provider=rerank_provider, top_k=2, timeout_seconds=30),
    )

    response = provider.query("payment terms", 2, [])

    assert response.retrieved_chunks[0].metadata["vector_retrieval_status"] == "failed"
    assert rerank_provider.documents == []


def test_summarize_results_averages_metrics_and_counts_failures() -> None:
    successful = evaluate_retrieval_response(
        make_case(),
        make_response([make_chunk("Payment terms: Net 15")]),
        "keyword",
        latency_ms=10.0,
    )
    failed = evaluate_retrieval_response(
        make_case(),
        make_response(
            [
                make_chunk(
                    "Payment terms: Net 15",
                    metadata={
                        "vector_retrieval_status": "failed",
                        "vector_retrieval_error": "Vector search returned no chunks.",
                    },
                )
            ]
        ),
        "vector",
        latency_ms=30.0,
    )

    summary = summarize_results([successful, failed])

    assert summary.hit_rate_at_k == 1.0
    assert summary.mrr_at_k == 1.0
    assert summary.recall_at_k == 0.5
    assert summary.average_latency_ms == 20.0
    assert summary.failure_count == 1
    assert summary.fallback_count == 1
    assert summary.trace_metadata_count == 1
    assert summary.result_strategy_counts == {"keyword": 1, "vector_unavailable_fallback": 1}
    assert summary.fallback_reasons == [{"reason": "Vector search returned no chunks.", "count": 1}]


def test_summarize_results_counts_hybrid_branch_fallback_without_failure() -> None:
    hybrid_fallback = evaluate_retrieval_response(
        make_case(),
        make_response(
            [
                make_chunk(
                    "Payment terms: Net 15",
                    metadata={
                        "strategy_label": "hybrid",
                        "branch_failures": "vector",
                        "fallback_reason": "Qdrant unavailable",
                    },
                )
            ]
        ),
        "hybrid",
        latency_ms=10.0,
    )

    summary = summarize_results([hybrid_fallback])

    assert summary.failure_count == 0
    assert summary.fallback_count == 1
    assert summary.trace_metadata_count == 1
    assert summary.result_strategy_counts == {"hybrid": 1}
    assert summary.fallback_reasons == [
        {"reason": "Qdrant unavailable", "count": 1},
        {"reason": "branch_failures=vector", "count": 1},
    ]
