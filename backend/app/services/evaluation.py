from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
from pathlib import Path
from time import perf_counter
from typing import Literal
from uuid import uuid4

from app.core.config import Settings, get_settings
from app.schemas.documents import DocumentChunk, DocumentMetadata, DocumentStatus, OcrResult, OcrStatus
from app.schemas.rag import RagQueryResponse, RetrievedChunk
from app.services.embedding import create_embedding_provider
from app.services.rag import KeywordRagProvider, RagProvider, VectorRagProvider
from app.services.rerank import RerankResult, RerankService, create_rerank_service
from app.services.vector_indexing import VectorIndexingService
from app.services.vector_store import create_qdrant_vector_store


EvalStrategy = Literal["keyword", "vector", "vector_rerank", "hybrid", "hybrid_rerank"]
ResultStrategy = Literal[
    "keyword",
    "vector",
    "vector_rerank",
    "hybrid",
    "hybrid_rerank",
    "vector_unavailable_fallback",
]
BUILT_IN_RAG_EVAL_STRATEGY: EvalStrategy = "hybrid_rerank"
BUILT_IN_RAG_EVAL_DATASET_NAME = "zh_invoice_hybrid_rerank_v1"
BUILT_IN_RAG_EVAL_DATASET_FILENAME = "built-in-rag-eval-zh-invoices.json"


@dataclass(frozen=True)
class RetrievalEvalCase:
    id: str
    query: str
    top_k: int
    expected_document_filenames: list[str]
    expected_chunk_hints: list[str]
    expected_terms: list[str]
    tags: list[str]
    notes: str = ""

    @classmethod
    def from_mapping(cls, raw_case: object) -> RetrievalEvalCase:
        if not isinstance(raw_case, dict):
            raise ValueError("Eval case must be an object.")

        case_id = cls._required_string(raw_case, "id")
        query = cls._required_string(raw_case, "query")
        top_k = raw_case.get("top_k")
        if not isinstance(top_k, int) or top_k < 1 or top_k > 10:
            raise ValueError(f"Eval case '{case_id}' top_k must be an integer between 1 and 10.")

        return cls(
            id=case_id,
            query=query,
            top_k=top_k,
            expected_document_filenames=cls._required_string_list(raw_case, "expected_document_filenames", case_id),
            expected_chunk_hints=cls._required_string_list(raw_case, "expected_chunk_hints", case_id),
            expected_terms=cls._required_string_list(raw_case, "expected_terms", case_id),
            tags=cls._required_string_list(raw_case, "tags", case_id),
            notes=str(raw_case.get("notes") or ""),
        )

    @staticmethod
    def _required_string(raw_case: dict[str, object], field_name: str) -> str:
        value = raw_case.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Eval case field '{field_name}' must be a non-empty string.")
        return value

    @staticmethod
    def _required_string_list(raw_case: dict[str, object], field_name: str, case_id: str) -> list[str]:
        value = raw_case.get(field_name)
        if not isinstance(value, list) or not value:
            raise ValueError(f"Eval case '{case_id}' field '{field_name}' must be a non-empty list.")

        values = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise ValueError(f"Eval case '{case_id}' field '{field_name}' must contain only non-empty strings.")
            values.append(item)

        return values


@dataclass(frozen=True)
class RetrievalEvalResult:
    case_id: str
    query: str
    top_k: int
    strategy: ResultStrategy
    latency_ms: float
    hit: bool
    first_relevant_rank: int | None
    reciprocal_rank: float
    recall_at_k: float
    matched_expected_terms: list[str] = field(default_factory=list)
    retrieved_chunks: list[dict[str, object]] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "query": self.query,
            "top_k": self.top_k,
            "strategy": self.strategy,
            "latency_ms": round(self.latency_ms, 2),
            "hit": self.hit,
            "first_relevant_rank": self.first_relevant_rank,
            "reciprocal_rank": round(self.reciprocal_rank, 4),
            "recall_at_k": round(self.recall_at_k, 4),
            "matched_expected_terms": self.matched_expected_terms,
            "retrieved_chunks": self.retrieved_chunks,
            "error": self.error,
        }


@dataclass(frozen=True)
class RetrievalEvalSummary:
    case_count: int
    hit_rate_at_k: float
    mrr_at_k: float
    recall_at_k: float
    average_latency_ms: float
    failure_count: int
    fallback_count: int
    trace_metadata_count: int
    result_strategy_counts: dict[str, int] = field(default_factory=dict)
    fallback_reasons: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "case_count": self.case_count,
            "hit_rate_at_k": round(self.hit_rate_at_k, 4),
            "mrr_at_k": round(self.mrr_at_k, 4),
            "recall_at_k": round(self.recall_at_k, 4),
            "average_latency_ms": round(self.average_latency_ms, 2),
            "failure_count": self.failure_count,
            "fallback_count": self.fallback_count,
            "trace_metadata_count": self.trace_metadata_count,
            "result_strategy_counts": self.result_strategy_counts,
            "fallback_reasons": self.fallback_reasons,
        }


@dataclass(frozen=True)
class RetrievalEvalRun:
    run_id: str
    created_at: str
    strategy: EvalStrategy
    dataset_path: str
    case_count: int
    summary: RetrievalEvalSummary
    results: list[RetrievalEvalResult]
    environment: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "strategy": self.strategy,
            "dataset_path": self.dataset_path,
            "case_count": self.case_count,
            "summary": self.summary.to_dict(),
            "results": [result.to_dict() for result in self.results],
            "environment": self.environment,
        }


def load_eval_cases(dataset_path: Path) -> list[RetrievalEvalCase]:
    raw_dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(raw_dataset, list):
        raise ValueError("Retrieval eval dataset must be a JSON array.")

    cases = [RetrievalEvalCase.from_mapping(raw_case) for raw_case in raw_dataset]
    case_ids = [case.id for case in cases]
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("Retrieval eval dataset contains duplicate case ids.")

    return cases


def build_eval_documents(
    cases: list[RetrievalEvalCase],
    sample_documents_dir: Path,
) -> list[DocumentMetadata]:
    filenames = sorted(
        {
            filename
            for case in cases
            for filename in case.expected_document_filenames
        }
    )
    created_at = datetime(2026, 5, 22, tzinfo=UTC)
    documents = []

    for filename in filenames:
        sample_path = sample_documents_dir / filename
        if not sample_path.is_file():
            raise FileNotFoundError(f"Eval sample document '{filename}' was not found at {sample_path}.")

        text = sample_path.read_text(encoding="utf-8")
        document_id = f"eval-{sample_path.stem.lower().replace('_', '-')}"
        chunks = _build_line_chunks(document_id, text, created_at)
        documents.append(
            DocumentMetadata(
                document_id=document_id,
                filename=filename,
                stored_filename=filename,
                file_type=sample_path.suffix.lstrip(".") or "txt",
                content_type="text/plain",
                size=len(text.encode("utf-8")),
                status=DocumentStatus.READY,
                created_at=created_at,
                ocr=OcrResult(status=OcrStatus.COMPLETED, text=text, updated_at=created_at),
                chunks=chunks,
            )
        )

    return documents


def run_retrieval_eval(
    cases: list[RetrievalEvalCase],
    documents: list[DocumentMetadata],
    provider: RagProvider,
    strategy: EvalStrategy,
    dataset_path: Path,
    environment: dict[str, object] | None = None,
) -> RetrievalEvalRun:
    results: list[RetrievalEvalResult] = []

    for case in cases:
        started_at = perf_counter()
        try:
            response = provider.query(case.query, case.top_k, documents)
        except Exception as exc:
            latency_ms = (perf_counter() - started_at) * 1000
            results.append(_failed_result(case, strategy, latency_ms, str(exc)))
            continue

        latency_ms = (perf_counter() - started_at) * 1000
        results.append(evaluate_retrieval_response(case, response, strategy, latency_ms))

    return RetrievalEvalRun(
        run_id=str(uuid4()),
        created_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        strategy=strategy,
        dataset_path=str(dataset_path),
        case_count=len(cases),
        summary=summarize_results(results),
        results=results,
        environment=environment or {},
    )


class VectorRerankEvalProvider:
    name = "vector_rerank"

    def __init__(
        self,
        vector_provider: RagProvider,
        response_builder: KeywordRagProvider,
        rerank_service: RerankService,
    ) -> None:
        self.vector_provider = vector_provider
        self.response_builder = response_builder
        self.rerank_service = rerank_service

    def query(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> RagQueryResponse:
        vector_response = self.vector_provider.query(query, top_k, documents)
        if _vector_fallback_error(vector_response):
            return vector_response

        rerank_result = self.rerank_service.rerank(query, vector_response.retrieved_chunks)
        return self.response_builder.build_response(query, rerank_result.chunks)


class HybridEvalProvider:
    name = "hybrid"
    _fusion_rank_offset = 60

    def __init__(
        self,
        keyword_provider: KeywordRagProvider,
        vector_provider: RagProvider,
    ) -> None:
        self.keyword_provider = keyword_provider
        self.vector_provider = vector_provider

    def query(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> RagQueryResponse:
        keyword_chunks = self.keyword_provider.retrieve(query, top_k, documents)
        vector_response = self.vector_provider.query(query, top_k, documents)
        vector_error = _vector_fallback_error(vector_response)
        if vector_error:
            return self.keyword_provider.build_response(
                query,
                self._annotate_keyword_fallback(keyword_chunks, vector_error),
            )

        merged_chunks = self._merge_candidates(keyword_chunks, vector_response.retrieved_chunks, top_k)
        return self.keyword_provider.build_response(query, merged_chunks)

    def _annotate_keyword_fallback(
        self,
        keyword_chunks: list[RetrievedChunk],
        vector_error: str,
    ) -> list[RetrievedChunk]:
        metadata = {
            "strategy_label": "hybrid",
            "hybrid_enabled": "true",
            "merge_policy": "rank_based_fusion",
            "branch_failures": "vector",
            "fallback_reason": vector_error,
            "vector_retrieval_status": "failed",
            "vector_retrieval_error": vector_error,
            "keyword_candidate_count": str(len(keyword_chunks)),
            "vector_candidate_count": "0",
            "merged_candidate_count": str(len(keyword_chunks)),
            "deduped_candidate_count": "0",
        }
        return [
            chunk.model_copy(
                update={
                    "metadata": {
                        **chunk.metadata,
                        **metadata,
                        "branches": "keyword",
                        "final_rank": str(rank),
                        "keyword_rank": str(rank),
                        "keyword_score": f"{chunk.score:.6f}",
                    }
                }
            )
            for rank, chunk in enumerate(keyword_chunks, start=1)
        ]

    def _merge_candidates(
        self,
        keyword_chunks: list[RetrievedChunk],
        vector_chunks: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        candidates: dict[str, dict[str, object]] = {}

        for branch_name, chunks in (("keyword", keyword_chunks), ("vector", vector_chunks)):
            for rank, chunk in enumerate(chunks, start=1):
                key, key_fallback = _candidate_dedupe_key(chunk)
                candidate = candidates.setdefault(
                    key,
                    {
                        "chunk": chunk,
                        "branches": [],
                        "score": 0.0,
                        "best_rank": rank,
                        "dedupe_key": key,
                        "dedupe_key_fallback": key_fallback,
                    },
                )
                branches = candidate["branches"]
                assert isinstance(branches, list)
                if branch_name not in branches:
                    branches.append(branch_name)
                candidate["score"] = float(candidate["score"]) + self._fusion_score(rank)
                candidate["best_rank"] = min(int(candidate["best_rank"]), rank)
                candidate[f"{branch_name}_rank"] = rank
                candidate[f"{branch_name}_score"] = chunk.score

                if branch_name == "keyword":
                    candidate["chunk"] = chunk

        merged_candidates = sorted(
            candidates.values(),
            key=lambda candidate: (
                -float(candidate["score"]),
                int(candidate["best_rank"]),
                str(candidate["dedupe_key"]),
            ),
        )
        deduped_count = len(keyword_chunks) + len(vector_chunks) - len(merged_candidates)

        merged_chunks = []
        for final_rank, candidate in enumerate(merged_candidates[:top_k], start=1):
            chunk = candidate["chunk"]
            assert isinstance(chunk, RetrievedChunk)
            branches = candidate["branches"]
            assert isinstance(branches, list)
            metadata = {
                **chunk.metadata,
                "strategy_label": "hybrid",
                "hybrid_enabled": "true",
                "merge_policy": "rank_based_fusion",
                "dedupe_key": str(candidate["dedupe_key"]),
                "dedupe_key_fallback": str(candidate["dedupe_key_fallback"]),
                "keyword_candidate_count": str(len(keyword_chunks)),
                "vector_candidate_count": str(len(vector_chunks)),
                "merged_candidate_count": str(len(merged_candidates)),
                "deduped_candidate_count": str(deduped_count),
                "branch_failures": "",
                "fallback_reason": "",
                "branches": ",".join(str(branch) for branch in branches),
                "final_rank": str(final_rank),
                "merged_score": f"{float(candidate['score']):.6f}",
            }

            if "keyword_rank" in candidate:
                metadata["keyword_rank"] = str(candidate["keyword_rank"])
                metadata["keyword_score"] = f"{float(candidate['keyword_score']):.6f}"
            if "vector_rank" in candidate:
                metadata["vector_rank"] = str(candidate["vector_rank"])
                metadata["vector_score"] = f"{float(candidate['vector_score']):.6f}"

            merged_chunks.append(
                chunk.model_copy(
                    update={
                        "score": float(candidate["score"]),
                        "metadata": metadata,
                    }
                )
            )

        return merged_chunks

    def _fusion_score(self, rank: int) -> float:
        return 1 / (rank + self._fusion_rank_offset)


class HybridRerankEvalProvider:
    name = "hybrid_rerank"

    def __init__(
        self,
        hybrid_provider: HybridEvalProvider,
        response_builder: KeywordRagProvider,
        rerank_service: RerankService,
    ) -> None:
        self.hybrid_provider = hybrid_provider
        self.response_builder = response_builder
        self.rerank_service = rerank_service

    def query(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> RagQueryResponse:
        hybrid_response = self.hybrid_provider.query(query, top_k, documents)
        rerank_result = self.rerank_service.rerank(query, hybrid_response.retrieved_chunks)
        reranked_chunks = self._annotate_hybrid_rerank_chunks(rerank_result)
        return self.response_builder.build_response(query, reranked_chunks)

    def _annotate_hybrid_rerank_chunks(self, rerank_result: RerankResult) -> list[RetrievedChunk]:
        annotated_chunks = []
        for final_rank, chunk in enumerate(rerank_result.chunks, start=1):
            fallback_state = self._fallback_state(chunk, rerank_result.status)
            merged_rank = chunk.metadata.get("final_rank", "")
            if chunk.metadata.get("rerank_score"):
                final_score_source = "rerank_score"
            elif chunk.metadata.get("merged_score"):
                final_score_source = "merged_score"
            elif chunk.metadata.get("keyword_score"):
                final_score_source = "keyword_score"
            else:
                final_score_source = "candidate_score"
            annotated_chunks.append(
                chunk.model_copy(
                    update={
                        "metadata": {
                            **chunk.metadata,
                            "strategy_label": "hybrid_rerank",
                            "candidate_flow": "keyword+vector -> hybrid_merge -> rerank",
                            "hybrid_candidate_count": str(rerank_result.input_candidate_count),
                            "rerank_input_count": str(rerank_result.input_candidate_count),
                            "final_candidate_count": str(len(rerank_result.chunks)),
                            "merged_rank": str(merged_rank),
                            "final_rank": str(final_rank),
                            "final_score": f"{chunk.score:.6f}",
                            "final_score_source": final_score_source,
                            "rerank_provider": rerank_result.provider,
                            "rerank_model": str(rerank_result.model or ""),
                            "rerank_status": rerank_result.status,
                            "rerank_top_k": str(rerank_result.rerank_top_k),
                            "fallback_state": fallback_state,
                        },
                    }
                )
            )

        return annotated_chunks

    def _fallback_state(self, chunk: RetrievedChunk, rerank_status: str) -> str:
        if rerank_status == "disabled":
            return "reranker_disabled"
        if rerank_status == "failed":
            return "reranker_unavailable"
        if chunk.metadata.get("vector_retrieval_status") == "failed":
            return "vector_unavailable"
        return "none"


class UnavailableVectorEvalProvider:
    name = "vector_unavailable"

    def __init__(
        self,
        keyword_provider: KeywordRagProvider,
        reason: str,
        settings: Settings,
    ) -> None:
        self.keyword_provider = keyword_provider
        self.reason = reason
        self.settings = settings

    def query(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> RagQueryResponse:
        response = self.keyword_provider.query(query, top_k, documents)
        fallback_metadata = {
            "retrieval_provider": "keyword",
            "vector_retrieval_status": "failed",
            "vector_store": "qdrant",
            "qdrant_collection": self.settings.qdrant_collection,
            "embedding_provider": str(self.settings.embedding_provider or "disabled"),
            "embedding_model": self.settings.embedding_model,
            "vector_retrieval_error": self.reason[:500],
        }
        citations = [
            citation.model_copy(
                update={
                    "trace_metadata": {
                        **citation.trace_metadata,
                        **fallback_metadata,
                    }
                }
            )
            for citation in response.citations
        ]
        retrieved_chunks = [
            chunk.model_copy(
                update={
                    "metadata": {
                        **chunk.metadata,
                        **fallback_metadata,
                    }
                }
            )
            for chunk in response.retrieved_chunks
        ]
        return response.model_copy(
            update={
                "answer": (
                    f"{response.answer}\n\n"
                    f"Vector retrieval unavailable; fallback to keyword retrieval. Error: {self.reason}"
                ),
                "citations": citations,
                "retrieved_chunks": retrieved_chunks,
            }
        )


def evaluate_retrieval_response(
    case: RetrievalEvalCase,
    response: RagQueryResponse,
    strategy: EvalStrategy,
    latency_ms: float,
) -> RetrievalEvalResult:
    expected_documents = {filename.casefold() for filename in case.expected_document_filenames}
    first_relevant_rank: int | None = None
    matched_expected_terms: list[str] = []

    for rank, chunk in enumerate(response.retrieved_chunks[: case.top_k], start=1):
        if expected_documents and chunk.filename.casefold() not in expected_documents:
            continue

        chunk_matched_terms = _matched_values(case.expected_terms, chunk)
        chunk_matched_hints = _matched_values(case.expected_chunk_hints, chunk)

        for term in chunk_matched_terms:
            if term not in matched_expected_terms:
                matched_expected_terms.append(term)

        if first_relevant_rank is None and (chunk_matched_terms or chunk_matched_hints):
            first_relevant_rank = rank

    reciprocal_rank = 0.0 if first_relevant_rank is None else 1 / first_relevant_rank
    recall_at_k = _recall_at_k(case, matched_expected_terms, response.retrieved_chunks[: case.top_k])
    fallback_error = _vector_fallback_error(response)
    result_error = fallback_error if strategy in {"vector", "vector_rerank"} else None

    return RetrievalEvalResult(
        case_id=case.id,
        query=case.query,
        top_k=case.top_k,
        strategy="vector_unavailable_fallback" if result_error else strategy,
        latency_ms=latency_ms,
        hit=first_relevant_rank is not None,
        first_relevant_rank=first_relevant_rank,
        reciprocal_rank=reciprocal_rank,
        recall_at_k=recall_at_k,
        matched_expected_terms=matched_expected_terms,
        retrieved_chunks=_retrieved_chunks_output(response.retrieved_chunks[: case.top_k]),
        error=result_error,
    )


def summarize_results(results: list[RetrievalEvalResult]) -> RetrievalEvalSummary:
    if not results:
        return RetrievalEvalSummary(
            case_count=0,
            hit_rate_at_k=0.0,
            mrr_at_k=0.0,
            recall_at_k=0.0,
            average_latency_ms=0.0,
            failure_count=0,
            fallback_count=0,
            trace_metadata_count=0,
        )

    count = len(results)
    result_strategy_counts: dict[str, int] = {}
    fallback_reason_counts: dict[str, int] = {}
    fallback_count = 0
    trace_metadata_count = 0

    for result in results:
        result_strategy_counts[result.strategy] = result_strategy_counts.get(result.strategy, 0) + 1
        trace_metadata_count += _trace_metadata_count(result)
        fallback_reasons = _result_fallback_reasons(result)

        if fallback_reasons:
            fallback_count += 1

        for reason in fallback_reasons:
            fallback_reason_counts[reason] = fallback_reason_counts.get(reason, 0) + 1

    return RetrievalEvalSummary(
        case_count=count,
        hit_rate_at_k=sum(1 for result in results if result.hit) / count,
        mrr_at_k=sum(result.reciprocal_rank for result in results) / count,
        recall_at_k=sum(result.recall_at_k for result in results) / count,
        average_latency_ms=sum(result.latency_ms for result in results) / count,
        failure_count=sum(1 for result in results if result.error),
        fallback_count=fallback_count,
        trace_metadata_count=trace_metadata_count,
        result_strategy_counts=dict(sorted(result_strategy_counts.items())),
        fallback_reasons=[
            {"reason": reason, "count": fallback_reason_counts[reason]}
            for reason in sorted(fallback_reason_counts)
        ],
    )


def create_eval_provider(
    strategy: EvalStrategy,
    documents: list[DocumentMetadata],
    settings: Settings,
) -> tuple[RagProvider, dict[str, object]]:
    keyword_provider = KeywordRagProvider()
    if strategy == "keyword":
        return keyword_provider, {"retrieval_provider": "keyword"}

    embedding_provider = create_embedding_provider(settings)
    embedding_health = embedding_provider.check_health()
    if not embedding_health.available:
        raise RuntimeError(f"Vector eval requires available embedding provider. {embedding_health.message}")

    vector_store = create_qdrant_vector_store(settings)
    collection = vector_store.ensure_collection()
    indexing_service = VectorIndexingService(embedding_provider, vector_store)
    indexing_results = [indexing_service.index_document(document) for document in documents]
    failed_indexing = [result for result in indexing_results if result.status != "completed"]
    if failed_indexing:
        details = "; ".join(result.error or result.reason or result.status for result in failed_indexing)
        raise RuntimeError(f"Vector eval manual indexing did not complete. {details}")

    vector_provider = VectorRagProvider(keyword_provider, embedding_provider, vector_store)
    environment = {
        "retrieval_provider": strategy,
        "embedding_provider": embedding_provider.name,
        "embedding_model": str(getattr(embedding_provider, "model", "unknown")),
        "qdrant_collection": vector_store.collection_name,
        "qdrant_vector_size": vector_store.vector_size,
        "qdrant_collection_exists": collection.exists,
        "indexed_document_count": len(indexing_results),
        "indexed_chunk_count": sum(result.indexed_chunk_count for result in indexing_results),
    }

    if strategy == "vector":
        return vector_provider, environment

    if strategy in {"hybrid", "hybrid_rerank"}:
        environment.update(
            {
                "merge_policy": "rank_based_fusion",
                "dedupe_key": "document_id_chunk_id",
            }
        )
    if strategy == "hybrid":
        return HybridEvalProvider(keyword_provider, vector_provider), environment

    rerank_service = create_rerank_service(settings)
    environment.update(
        {
            "rerank_provider": rerank_service.provider.name,
            "rerank_model": str(rerank_service.provider.model or ""),
            "rerank_top_k": rerank_service.top_k,
            "rerank_timeout_seconds": rerank_service.timeout_seconds,
        }
    )
    if strategy == "hybrid_rerank":
        return HybridRerankEvalProvider(
            HybridEvalProvider(keyword_provider, vector_provider),
            keyword_provider,
            rerank_service,
        ), environment

    return VectorRerankEvalProvider(vector_provider, keyword_provider, rerank_service), environment


def built_in_rag_eval_dataset_path(repo_root: Path | None = None) -> Path:
    root = repo_root or default_repo_root()
    return root / "sample-data" / "eval" / BUILT_IN_RAG_EVAL_DATASET_FILENAME


def run_built_in_rag_eval(settings: Settings, repo_root: Path | None = None) -> RetrievalEvalRun:
    root = repo_root or default_repo_root()
    dataset_path = built_in_rag_eval_dataset_path(root)
    cases = load_eval_cases(dataset_path)
    documents = build_eval_documents(cases, root / "sample-data" / "documents")
    provider, environment = create_built_in_hybrid_rerank_provider(documents, settings)
    environment = {
        **environment,
        "dataset_name": BUILT_IN_RAG_EVAL_DATASET_NAME,
        "document_fixture_count": len({filename for case in cases for filename in case.expected_document_filenames}),
        "case_count": len(cases),
    }
    return run_retrieval_eval(
        cases=cases,
        documents=documents,
        provider=provider,
        strategy=BUILT_IN_RAG_EVAL_STRATEGY,
        dataset_path=dataset_path,
        environment=environment,
    )


def create_built_in_hybrid_rerank_provider(
    documents: list[DocumentMetadata],
    settings: Settings,
) -> tuple[RagProvider, dict[str, object]]:
    eval_settings = _built_in_eval_settings(settings)
    keyword_provider = KeywordRagProvider()
    embedding_provider = create_embedding_provider(eval_settings)
    vector_store = create_qdrant_vector_store(eval_settings)
    environment: dict[str, object] = {
        "retrieval_provider": BUILT_IN_RAG_EVAL_STRATEGY,
        "fallback_safe": True,
        "embedding_provider": embedding_provider.name,
        "embedding_model": str(getattr(embedding_provider, "model", eval_settings.embedding_model)),
        "qdrant_collection": vector_store.collection_name,
        "qdrant_vector_size": vector_store.vector_size,
        "merge_policy": "rank_based_fusion",
        "dedupe_key": "document_id_chunk_id",
    }

    vector_provider: RagProvider | None = None
    embedding_health = embedding_provider.check_health()
    environment.update(
        {
            "embedding_health_available": embedding_health.available,
            "embedding_health_message": embedding_health.message,
        }
    )

    if not embedding_health.available:
        reason = embedding_health.message
        vector_provider = UnavailableVectorEvalProvider(keyword_provider, reason, eval_settings)
        environment.update(
            {
                "vector_preflight_status": "failed",
                "vector_preflight_reason": reason,
                "indexed_document_count": 0,
                "indexed_chunk_count": 0,
            }
        )
    else:
        try:
            collection = vector_store.ensure_collection()
            indexing_service = VectorIndexingService(embedding_provider, vector_store)
            indexing_results = [indexing_service.index_document(document) for document in documents]
            failed_indexing = [result for result in indexing_results if result.status != "completed"]
            if failed_indexing:
                details = "; ".join(result.error or result.reason or result.status for result in failed_indexing)
                raise RuntimeError(f"Built-in eval vector indexing did not complete. {details}")

            vector_provider = VectorRagProvider(keyword_provider, embedding_provider, vector_store)
            environment.update(
                {
                    "vector_preflight_status": "completed",
                    "qdrant_collection_exists": collection.exists,
                    "indexed_document_count": len(indexing_results),
                    "indexed_chunk_count": sum(result.indexed_chunk_count for result in indexing_results),
                }
            )
        except Exception as exc:
            reason = str(exc)
            vector_provider = UnavailableVectorEvalProvider(keyword_provider, reason, eval_settings)
            environment.update(
                {
                    "vector_preflight_status": "failed",
                    "vector_preflight_reason": reason,
                    "indexed_document_count": 0,
                    "indexed_chunk_count": 0,
                }
            )

    rerank_service = create_rerank_service(eval_settings)
    environment.update(
        {
            "rerank_provider": rerank_service.provider.name,
            "rerank_model": str(rerank_service.provider.model or ""),
            "rerank_top_k": rerank_service.top_k,
            "rerank_timeout_seconds": rerank_service.timeout_seconds,
        }
    )
    return (
        HybridRerankEvalProvider(
            HybridEvalProvider(keyword_provider, vector_provider),
            keyword_provider,
            rerank_service,
        ),
        environment,
    )


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> int:
    repo_root = default_repo_root()
    parser = argparse.ArgumentParser(description="Run DocuRAG retrieval evaluation baseline.")
    parser.add_argument(
        "--strategy",
        choices=["keyword", "vector", "vector_rerank", "hybrid", "hybrid_rerank"],
        default="keyword",
    )
    parser.add_argument("--dataset", type=Path, default=repo_root / "sample-data/eval/retrieval-eval.json")
    parser.add_argument("--sample-documents", type=Path, default=repo_root / "sample-data/documents")
    parser.add_argument("--output", type=Path, default=repo_root / ".tmp/retrieval-eval-result.json")
    args = parser.parse_args()

    cases = load_eval_cases(args.dataset)
    documents = build_eval_documents(cases, args.sample_documents)
    provider, environment = create_eval_provider(args.strategy, documents, get_settings())
    run = run_retrieval_eval(cases, documents, provider, args.strategy, args.dataset, environment)
    output = run.to_dict()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = output["summary"]
    print(
        "Retrieval eval summary: "
        f"strategy={args.strategy}, "
        f"cases={output['case_count']}, "
        f"hit_rate_at_k={summary['hit_rate_at_k']}, "
        f"mrr_at_k={summary['mrr_at_k']}, "
        f"recall_at_k={summary['recall_at_k']}, "
        f"average_latency_ms={summary['average_latency_ms']}, "
        f"failure_count={summary['failure_count']}, "
        f"fallback_count={summary['fallback_count']}, "
        f"trace_metadata_count={summary['trace_metadata_count']}, "
        f"result_strategy_counts={summary['result_strategy_counts']}"
    )
    if summary["fallback_reasons"]:
        print(f"Fallback reasons: {summary['fallback_reasons']}")
    print(f"Result JSON: {args.output}")
    return 0


def _build_line_chunks(document_id: str, text: str, created_at: datetime) -> list[DocumentChunk]:
    chunks = []
    for line in text.splitlines():
        clean_line = line.strip()
        if not clean_line:
            continue

        chunks.append(
            DocumentChunk(
                chunk_id=f"{document_id}-chunk-{len(chunks) + 1:03d}",
                document_id=document_id,
                text=clean_line,
                source="eval_fixture",
                created_at=created_at,
                source_type="eval_fixture",
                metadata={"origin": "eval_fixture", "provider": "eval_fixture"},
            )
        )

    return chunks


def _matched_values(expected_values: list[str], chunk: RetrievedChunk) -> list[str]:
    text = f"{chunk.filename}\n{chunk.chunk_id}\n{chunk.text}".casefold()
    return [value for value in expected_values if value.casefold() in text]


def _recall_at_k(
    case: RetrievalEvalCase,
    matched_expected_terms: list[str],
    retrieved_chunks: list[RetrievedChunk],
) -> float:
    if case.expected_terms:
        return len(matched_expected_terms) / len(case.expected_terms)

    matched_hints = {
        hint
        for chunk in retrieved_chunks
        for hint in _matched_values(case.expected_chunk_hints, chunk)
    }
    if case.expected_chunk_hints:
        return len(matched_hints) / len(case.expected_chunk_hints)

    expected_documents = {filename.casefold() for filename in case.expected_document_filenames}
    matched_documents = {
        chunk.filename.casefold()
        for chunk in retrieved_chunks
        if chunk.filename.casefold() in expected_documents
    }
    return len(matched_documents) / len(expected_documents) if expected_documents else 0.0


def _vector_fallback_error(response: RagQueryResponse) -> str | None:
    for chunk in response.retrieved_chunks:
        if chunk.metadata.get("vector_retrieval_status") == "failed":
            return chunk.metadata.get("vector_retrieval_error") or "vector retrieval unavailable"

    for citation in response.citations:
        if citation.trace_metadata.get("vector_retrieval_status") == "failed":
            return citation.trace_metadata.get("vector_retrieval_error") or "vector retrieval unavailable"

    return None


def _candidate_dedupe_key(chunk: RetrievedChunk) -> tuple[str, str]:
    if chunk.document_id and chunk.chunk_id:
        return f"{chunk.document_id}:{chunk.chunk_id}", ""

    normalized_text = " ".join(chunk.text.casefold().split())
    if chunk.document_id and normalized_text:
        return f"{chunk.document_id}:{normalized_text}", "document_text"

    return f"{chunk.filename}:{normalized_text}", "unavailable"


def _retrieved_chunks_output(chunks: list[RetrievedChunk]) -> list[dict[str, object]]:
    return [
        {
            "rank": rank,
            "document_id": chunk.document_id,
            "filename": chunk.filename,
            "chunk_id": chunk.chunk_id,
            "score": chunk.score,
            "text": chunk.text,
            "source": chunk.source,
            "metadata": chunk.metadata,
        }
        for rank, chunk in enumerate(chunks, start=1)
    ]


def _trace_metadata_count(result: RetrievalEvalResult) -> int:
    return sum(
        1
        for chunk in result.retrieved_chunks
        if isinstance(chunk.get("metadata"), dict) and bool(chunk["metadata"])
    )


def _result_fallback_reasons(result: RetrievalEvalResult) -> list[str]:
    reasons: list[str] = []

    if result.error:
        reasons.append(result.error)

    for chunk in result.retrieved_chunks:
        metadata = chunk.get("metadata")
        if not isinstance(metadata, dict):
            continue

        for key in ("fallback_reason", "rerank_fallback_reason", "vector_retrieval_error"):
            value = metadata.get(key)
            if value:
                reasons.append(str(value))

        branch_failures = metadata.get("branch_failures")
        if branch_failures:
            reasons.append(f"branch_failures={branch_failures}")

        if metadata.get("vector_retrieval_status") == "failed" and not metadata.get("vector_retrieval_error"):
            reasons.append("vector retrieval unavailable")

        rerank_status = metadata.get("rerank_status")
        if rerank_status in {"disabled", "failed"} and not metadata.get("rerank_fallback_reason"):
            reasons.append(f"rerank_status={rerank_status}")

    return list(dict.fromkeys(reasons))


def result_fallback_reasons(result: RetrievalEvalResult) -> list[str]:
    return _result_fallback_reasons(result)


def _built_in_eval_settings(settings: Settings) -> Settings:
    return settings.model_copy(
        update={
            "embedding_timeout_seconds": min(settings.embedding_timeout_seconds, 2.0),
            "qdrant_timeout_seconds": min(settings.qdrant_timeout_seconds, 2.0),
        }
    )


def _failed_result(
    case: RetrievalEvalCase,
    strategy: EvalStrategy,
    latency_ms: float,
    error: str,
) -> RetrievalEvalResult:
    return RetrievalEvalResult(
        case_id=case.id,
        query=case.query,
        top_k=case.top_k,
        strategy=strategy,
        latency_ms=latency_ms,
        hit=False,
        first_relevant_rank=None,
        reciprocal_rank=0.0,
        recall_at_k=0.0,
        error=error,
    )


if __name__ == "__main__":
    raise SystemExit(main())
