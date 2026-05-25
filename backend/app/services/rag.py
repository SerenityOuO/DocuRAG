import re
from time import perf_counter
from typing import Protocol

from app.schemas.documents import DocumentMetadata
from app.schemas.rag import RagCitation, RagQueryResponse, RetrievedChunk
from app.services.embedding import EmbeddingProvider, EmbeddingProviderError
from app.services.llm import LlmGeneration, LlmProvider, LlmProviderError
from app.services.rerank import RerankResult, RerankService
from app.services.vector_store import QdrantVectorStore, QdrantVectorStoreError


QUERY_ALIASES = {
    "付款期限": ["payment", "due", "date", "terms", "net"],
    "付款日期": ["payment", "due", "date", "terms", "net"],
    "何時付款": ["payment", "due", "date", "terms", "net"],
    "什麼時候付款": ["payment", "due", "date", "terms", "net"],
    "繳款期限": ["payment", "due", "date", "terms", "net"],
    "付款條件": ["payment", "terms", "net"],
    "總金額": ["total", "amount", "invoice"],
    "金額多少": ["total", "amount", "invoice"],
    "發票號碼": ["invoice", "number"],
    "發票編號": ["invoice", "number"],
    "續約日期": ["renewal", "date"],
    "續約日": ["renewal", "date"],
    "回覆時間": ["sla", "response", "target"],
    "客服目標": ["sla", "response", "target"],
}


class RagProvider(Protocol):
    name: str

    def query(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> RagQueryResponse:
        pass


class KeywordRagProvider:
    name = "keyword"

    def __init__(self, llm_provider: LlmProvider | None = None) -> None:
        self.llm_provider = llm_provider

    def query(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> RagQueryResponse:
        retrieved_chunks = self.retrieve(query, top_k, documents)
        return self.build_response(query, retrieved_chunks)

    def build_response(
        self,
        query: str,
        retrieved_chunks: list[RetrievedChunk],
    ) -> RagQueryResponse:
        citations = [
            RagCitation(
                document_id=chunk.document_id,
                filename=chunk.filename,
                chunk_id=chunk.chunk_id,
                page_number=chunk.page_number,
                bbox=chunk.bbox,
                confidence=chunk.confidence,
                source_type=chunk.source_type,
                trace_metadata={"source": chunk.source, **chunk.metadata},
            )
            for chunk in retrieved_chunks
        ]

        if not retrieved_chunks:
            answer = (
                f"No OCR chunks matched query: {query}. "
                "Upload a document, run Mock OCR, then query again."
            )
        else:
            evidence_lines = [
                f"{index}. [{chunk.filename} / {chunk.chunk_id}] {chunk.text}"
                for index, chunk in enumerate(retrieved_chunks, start=1)
            ]
            answer = "Local OCR chunks matched the query:\n" + "\n".join(evidence_lines)

        llm_trace_metadata: dict[str, str] = {}
        if retrieved_chunks and self.llm_provider is not None:
            answer, llm_trace_metadata = self._generate_answer(query, retrieved_chunks, answer)

        if llm_trace_metadata:
            citations = [
                citation.model_copy(
                    update={
                        "trace_metadata": {
                            **citation.trace_metadata,
                            **llm_trace_metadata,
                        }
                    }
                )
                for citation in citations
            ]

        return RagQueryResponse(
            answer=answer,
            citations=citations,
            retrieved_chunks=retrieved_chunks,
        )

    def retrieve(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> list[RetrievedChunk]:
        query_terms = self._tokenize(query)

        if not query_terms:
            return []

        matches: list[RetrievedChunk] = []

        for document in documents:
            for chunk in document.chunks:
                chunk_terms = self._tokenize(chunk.text)
                score = sum(chunk_terms.count(term) for term in query_terms)

                if score <= 0:
                    continue

                matches.append(
                    RetrievedChunk(
                        **chunk.model_dump(),
                        filename=document.filename,
                        score=float(score),
                    )
                )

        return sorted(
            matches,
            key=lambda chunk: (-chunk.score, -chunk.created_at.timestamp(), chunk.chunk_id),
        )[:top_k]

    def _tokenize(self, text: str) -> list[str]:
        lowered_text = text.lower()
        tokens = re.findall(r"[a-z0-9]+", lowered_text)

        for cjk_text in re.findall(r"[\u3400-\u9fff]+", text):
            if len(cjk_text) == 1:
                tokens.append(cjk_text)
                continue

            tokens.extend(cjk_text[index : index + 2] for index in range(len(cjk_text) - 1))

        for phrase, aliases in QUERY_ALIASES.items():
            if phrase in text:
                tokens.extend(aliases)

        return tokens

    def _generate_answer(
        self,
        query: str,
        retrieved_chunks: list[RetrievedChunk],
        fallback_answer: str,
    ) -> tuple[str, dict[str, str]]:
        assert self.llm_provider is not None

        prompt = self._build_generation_prompt(query, retrieved_chunks)
        started_at = perf_counter()
        try:
            generation = self.llm_provider.generate(
                prompt,
                system=(
                    "You answer questions using only the supplied retrieved OCR chunks. "
                    "If the answer is not present in those chunks, say that the retrieved chunks do not contain enough information."
                ),
            )
        except LlmProviderError as exc:
            return (
                f"{fallback_answer}\n\nLLM generation unavailable; returning retrieved OCR chunks only. Error: {exc}",
                self._llm_failure_trace_metadata(str(exc)),
            )

        latency_ms = (perf_counter() - started_at) * 1000
        text = generation.text.strip()
        if not text:
            return (
                f"{fallback_answer}\n\nLLM generation unavailable; model returned an empty answer.",
                self._llm_failure_trace_metadata("model returned an empty answer"),
            )

        return text, self._llm_success_trace_metadata(generation, latency_ms, len(retrieved_chunks))

    def _build_generation_prompt(self, query: str, retrieved_chunks: list[RetrievedChunk]) -> str:
        evidence_blocks = []
        for index, chunk in enumerate(retrieved_chunks, start=1):
            page = chunk.page_number if chunk.page_number is not None else "unknown"
            evidence_blocks.append(
                "\n".join(
                    [
                        f"[{index}] filename={chunk.filename}",
                        f"document_id={chunk.document_id}",
                        f"chunk_id={chunk.chunk_id}",
                        f"page={page}",
                        f"text={chunk.text}",
                    ]
                )
            )

        return (
            "Use only the retrieved chunks below to answer the query. "
            "Do not add facts that are not present in the chunks. "
            "When possible, mention the supporting chunk numbers in the answer.\n\n"
            f"Query:\n{query}\n\n"
            "Retrieved chunks:\n"
            + "\n\n".join(evidence_blocks)
        )

    def _llm_success_trace_metadata(
        self,
        generation: LlmGeneration,
        latency_ms: float,
        chunk_count: int,
    ) -> dict[str, str]:
        fields = {
            "llm_generation_status": "completed",
            "llm_provider": self.llm_provider.name if self.llm_provider is not None else "unknown",
            "llm_model": generation.model,
            "llm_prompt_source": "retrieved_chunks",
            "llm_prompt_chunk_count": str(chunk_count),
            "llm_generation_latency_ms": f"{latency_ms:.2f}",
        }

        if generation.prompt_tokens is not None:
            fields["llm_prompt_tokens"] = str(generation.prompt_tokens)

        if generation.completion_tokens is not None:
            fields["llm_completion_tokens"] = str(generation.completion_tokens)

        if generation.total_duration_ms is not None:
            fields["llm_total_duration_ms"] = f"{generation.total_duration_ms:.2f}"

        if generation.load_duration_ms is not None:
            fields["llm_load_duration_ms"] = f"{generation.load_duration_ms:.2f}"

        return fields

    def _llm_failure_trace_metadata(self, error: str) -> dict[str, str]:
        provider_name = self.llm_provider.name if self.llm_provider is not None else "unknown"
        model = getattr(self.llm_provider, "model", None)
        fields = {
            "llm_generation_status": "failed",
            "llm_provider": provider_name,
            "llm_error": error[:500],
        }

        if model:
            fields["llm_model"] = str(model)

        return fields


class VectorRagProvider:
    name = "vector"

    def __init__(
        self,
        keyword_provider: KeywordRagProvider,
        embedding_provider: EmbeddingProvider,
        vector_store: QdrantVectorStore,
    ) -> None:
        self.keyword_provider = keyword_provider
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def query(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> RagQueryResponse:
        try:
            retrieved_chunks = self.retrieve(query, top_k, documents)
            if not retrieved_chunks:
                raise QdrantVectorStoreError("Vector search returned no chunks.")
        except (EmbeddingProviderError, QdrantVectorStoreError, TimeoutError, ValueError) as exc:
            return self._fallback_to_keyword(query, top_k, documents, str(exc))

        return self.keyword_provider.build_response(query, retrieved_chunks)

    def retrieve(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
    ) -> list[RetrievedChunk]:
        indexed_document_ids = {
            document.document_id
            for document in documents
            if document.chunks
        }
        if not indexed_document_ids:
            return []

        collection_status = self.vector_store.get_collection()
        if not collection_status.exists:
            raise QdrantVectorStoreError(f"Qdrant collection '{self.vector_store.collection_name}' is missing.")
        if collection_status.vector_size != self.vector_store.vector_size:
            raise QdrantVectorStoreError(
                f"Qdrant collection '{self.vector_store.collection_name}' vector size is {collection_status.vector_size}; expected {self.vector_store.vector_size}."
            )

        query_embedding = self.embedding_provider.embed(query)
        search_results = self.vector_store.search(query_embedding.embedding, top_k)
        retrieved_chunks = []
        for result in search_results:
            payload_document_id = result.payload.get("document_id")
            if payload_document_id is not None and str(payload_document_id) not in indexed_document_ids:
                continue

            retrieved_chunks.append(self._retrieved_chunk_from_payload(result.payload, result.score))

        return retrieved_chunks

    def _retrieved_chunk_from_payload(self, payload: dict[str, object], score: float) -> RetrievedChunk:
        required_fields = ["chunk_id", "document_id", "filename", "text", "source", "created_at"]
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            raise QdrantVectorStoreError(
                f"Qdrant payload missing required chunk fields: {', '.join(missing_fields)}."
            )

        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        return RetrievedChunk(
            chunk_id=str(payload["chunk_id"]),
            document_id=str(payload["document_id"]),
            filename=str(payload["filename"]),
            text=str(payload["text"]),
            source=str(payload["source"]),
            created_at=payload["created_at"],
            page_number=payload.get("page_number"),
            bbox=payload.get("bbox"),
            confidence=payload.get("confidence"),
            source_type=str(payload.get("source_type") or payload["source"]),
            metadata={
                **{str(key): str(value) for key, value in metadata.items()},
                "retrieval_provider": "vector",
                "vector_retrieval_status": "completed",
                "vector_store": "qdrant",
                "qdrant_collection": self.vector_store.collection_name,
                "embedding_provider": self.embedding_provider.name,
                "embedding_model": str(getattr(self.embedding_provider, "model", "unknown")),
                "vector_score": f"{score:.6f}",
            },
            score=score,
        )

    def _fallback_to_keyword(
        self,
        query: str,
        top_k: int,
        documents: list[DocumentMetadata],
        error: str,
    ) -> RagQueryResponse:
        response = self.keyword_provider.query(query, top_k, documents)
        fallback_metadata = {
            "retrieval_provider": "keyword",
            "vector_retrieval_status": "failed",
            "vector_store": "qdrant",
            "qdrant_collection": self.vector_store.collection_name,
            "embedding_provider": self.embedding_provider.name,
            "embedding_model": str(getattr(self.embedding_provider, "model", "unknown")),
            "vector_retrieval_error": error[:500],
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
                    f"Vector retrieval unavailable; fallback to keyword retrieval. Error: {error}"
                ),
                "citations": citations,
                "retrieved_chunks": retrieved_chunks,
            }
        )


class VectorRerankRagProvider:
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
        if vector_fallback_error(vector_response):
            return vector_response

        rerank_result = self.rerank_service.rerank(query, vector_response.retrieved_chunks)
        return self.response_builder.build_response(query, rerank_result.chunks)


class HybridRagProvider:
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
        vector_error = vector_fallback_error(vector_response)
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
                key, key_fallback = candidate_dedupe_key(chunk)
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


class HybridRerankRagProvider:
    name = "hybrid_rerank"

    def __init__(
        self,
        hybrid_provider: HybridRagProvider,
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


def vector_fallback_error(response: RagQueryResponse) -> str | None:
    for chunk in response.retrieved_chunks:
        if chunk.metadata.get("vector_retrieval_status") == "failed":
            return chunk.metadata.get("vector_retrieval_error") or "vector retrieval unavailable"

    for citation in response.citations:
        if citation.trace_metadata.get("vector_retrieval_status") == "failed":
            return citation.trace_metadata.get("vector_retrieval_error") or "vector retrieval unavailable"

    return None


def candidate_dedupe_key(chunk: RetrievedChunk) -> tuple[str, str]:
    if chunk.document_id and chunk.chunk_id:
        return f"{chunk.document_id}:{chunk.chunk_id}", ""

    normalized_text = " ".join(chunk.text.casefold().split())
    if chunk.document_id and normalized_text:
        return f"{chunk.document_id}:{normalized_text}", "document_text"

    return f"{chunk.filename}:{normalized_text}", "unavailable"
