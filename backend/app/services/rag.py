import re
from typing import Protocol

from app.schemas.documents import DocumentMetadata
from app.schemas.rag import RagCitation, RagQueryResponse, RetrievedChunk


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
                f"No OCR mock chunks matched query: {query}. "
                "Upload a document, run Mock OCR, then query again."
            )
        else:
            evidence_lines = [
                f"{index}. [{chunk.filename} / {chunk.chunk_id}] {chunk.text}"
                for index, chunk in enumerate(retrieved_chunks, start=1)
            ]
            answer = "Local OCR mock chunks matched the query:\n" + "\n".join(evidence_lines)

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
