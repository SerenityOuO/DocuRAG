import re
from time import perf_counter
from typing import Protocol

from app.schemas.documents import DocumentMetadata
from app.schemas.rag import RagCitation, RagQueryResponse, RetrievedChunk
from app.services.llm import LlmGeneration, LlmProvider, LlmProviderError


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
        return re.findall(r"[a-z0-9]+", text.lower())

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
