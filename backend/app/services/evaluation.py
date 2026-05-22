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
from app.services.rerank import RerankService, create_rerank_service
from app.services.vector_indexing import VectorIndexingService
from app.services.vector_store import create_qdrant_vector_store


EvalStrategy = Literal["keyword", "vector", "vector_rerank"]
ResultStrategy = Literal["keyword", "vector", "vector_rerank", "vector_unavailable_fallback"]


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
    hit_rate_at_k: float
    mrr_at_k: float
    recall_at_k: float
    average_latency_ms: float
    failure_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "hit_rate_at_k": round(self.hit_rate_at_k, 4),
            "mrr_at_k": round(self.mrr_at_k, 4),
            "recall_at_k": round(self.recall_at_k, 4),
            "average_latency_ms": round(self.average_latency_ms, 2),
            "failure_count": self.failure_count,
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

    return RetrievalEvalResult(
        case_id=case.id,
        query=case.query,
        top_k=case.top_k,
        strategy="vector_unavailable_fallback" if fallback_error and strategy in {"vector", "vector_rerank"} else strategy,
        latency_ms=latency_ms,
        hit=first_relevant_rank is not None,
        first_relevant_rank=first_relevant_rank,
        reciprocal_rank=reciprocal_rank,
        recall_at_k=recall_at_k,
        matched_expected_terms=matched_expected_terms,
        retrieved_chunks=_retrieved_chunks_output(response.retrieved_chunks[: case.top_k]),
        error=fallback_error,
    )


def summarize_results(results: list[RetrievalEvalResult]) -> RetrievalEvalSummary:
    if not results:
        return RetrievalEvalSummary(
            hit_rate_at_k=0.0,
            mrr_at_k=0.0,
            recall_at_k=0.0,
            average_latency_ms=0.0,
            failure_count=0,
        )

    count = len(results)
    return RetrievalEvalSummary(
        hit_rate_at_k=sum(1 for result in results if result.hit) / count,
        mrr_at_k=sum(result.reciprocal_rank for result in results) / count,
        recall_at_k=sum(result.recall_at_k for result in results) / count,
        average_latency_ms=sum(result.latency_ms for result in results) / count,
        failure_count=sum(1 for result in results if result.error),
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
        "retrieval_provider": "vector" if strategy == "vector" else "vector_rerank",
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

    rerank_service = create_rerank_service(settings)
    environment.update(
        {
            "rerank_provider": rerank_service.provider.name,
            "rerank_model": str(rerank_service.provider.model or ""),
            "rerank_top_k": rerank_service.top_k,
            "rerank_timeout_seconds": rerank_service.timeout_seconds,
        }
    )
    return VectorRerankEvalProvider(vector_provider, keyword_provider, rerank_service), environment


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> int:
    repo_root = default_repo_root()
    parser = argparse.ArgumentParser(description="Run DocuRAG retrieval evaluation baseline.")
    parser.add_argument("--strategy", choices=["keyword", "vector", "vector_rerank"], default="keyword")
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
        f"failure_count={summary['failure_count']}"
    )
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
