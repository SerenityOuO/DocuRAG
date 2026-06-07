from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from app.schemas.documents import ChunkingStrategy, DocumentChunk, DocumentMetadata
from app.services.embedding import EmbeddingProvider, EmbeddingProviderError
from app.services.vector_store import QdrantPoint, QdrantVectorStore, QdrantVectorStoreError


VectorIndexingStatus = Literal["completed", "skipped", "failed"]
CHUNKING_VERSION = "v1"
FIXED_SIZE_MAX_CHARS = 360


@dataclass(frozen=True)
class VectorIndexingResult:
    document_id: str
    status: VectorIndexingStatus
    chunking_strategy: ChunkingStrategy = "fixed_size"
    chunking_version: str = CHUNKING_VERSION
    indexed_chunk_count: int = 0
    skipped_chunk_count: int = 0
    point_ids: list[str] = field(default_factory=list)
    collection_name: str | None = None
    vector_size: int | None = None
    embedding_provider: str | None = None
    embedding_model: str | None = None
    reason: str | None = None
    error: str | None = None


class VectorIndexingService:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: QdrantVectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def index_document(
        self,
        document: DocumentMetadata,
        chunking_strategy: ChunkingStrategy = "fixed_size",
    ) -> VectorIndexingResult:
        source_chunks = [chunk for chunk in document.chunks if chunk.text.strip()]
        skipped_chunk_count = len(document.chunks) - len(source_chunks)
        chunks = self._chunks_for_indexing(source_chunks, chunking_strategy)

        if not chunks:
            return self._skipped_result(
                document.document_id,
                chunking_strategy=chunking_strategy,
                skipped_chunk_count=len(document.chunks),
                reason="Document has no chunks to index.",
            )

        try:
            self._check_collection()
            points = [self._point_from_chunk(document, chunk) for chunk in chunks]
            self.vector_store.upsert_points(points)
        except (EmbeddingProviderError, QdrantVectorStoreError, TimeoutError, ValueError) as exc:
            return self._failed_result(
                document.document_id,
                chunking_strategy=chunking_strategy,
                skipped_chunk_count=skipped_chunk_count,
                error=str(exc),
            )

        return VectorIndexingResult(
            document_id=document.document_id,
            status="completed",
            chunking_strategy=chunking_strategy,
            chunking_version=CHUNKING_VERSION,
            indexed_chunk_count=len(points),
            skipped_chunk_count=skipped_chunk_count,
            point_ids=[point.point_id for point in points],
            collection_name=self.vector_store.collection_name,
            vector_size=self.vector_store.vector_size,
            embedding_provider=self.embedding_provider.name,
            embedding_model=str(getattr(self.embedding_provider, "model", "unknown")),
        )

    def point_id_for_chunk(self, document_id: str, chunk_id: str) -> str:
        return str(uuid5(NAMESPACE_URL, f"docurag:{document_id}:{chunk_id}"))

    def _chunks_for_indexing(
        self,
        chunks: list[DocumentChunk],
        chunking_strategy: ChunkingStrategy,
    ) -> list[DocumentChunk]:
        if chunking_strategy == "semantic":
            return self._semantic_chunks(chunks)

        return self._fixed_size_chunks(chunks, requested_strategy="fixed_size")

    def _fixed_size_chunks(
        self,
        chunks: list[DocumentChunk],
        requested_strategy: ChunkingStrategy,
        fallback_reason: str | None = None,
        start_index: int = 1,
    ) -> list[DocumentChunk]:
        indexed_chunks: list[DocumentChunk] = []

        for chunk in chunks:
            parts = self._split_fixed_size(chunk.text)
            for part_index, part in enumerate(parts, start=1):
                chunk_id = chunk.chunk_id if len(parts) == 1 else f"{chunk.chunk_id}:fixed:{part_index:03d}"
                indexed_chunks.append(
                    self._chunk_with_strategy_metadata(
                        chunk,
                        chunk_id,
                        part,
                        requested_strategy,
                        start_index + len(indexed_chunks),
                        {
                            "source_chunk_id": chunk.chunk_id,
                            "chunk_part_index": str(part_index),
                            **({"chunking_fallback_reason": fallback_reason} if fallback_reason else {}),
                        },
                    )
                )

        return indexed_chunks

    def _semantic_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        indexed_chunks: list[DocumentChunk] = []

        for chunk in chunks:
            segments = self._semantic_segments(chunk.text)
            if len(segments) <= 1:
                indexed_chunks.extend(
                    self._fixed_size_chunks(
                        [chunk],
                        requested_strategy="semantic",
                        fallback_reason="semantic_boundaries_unavailable",
                        start_index=len(indexed_chunks) + 1,
                    )
                )
                continue

            for segment_index, segment in enumerate(segments, start=1):
                segment_parts = self._split_fixed_size(segment)
                for part_index, part in enumerate(segment_parts, start=1):
                    chunk_id = (
                        f"{chunk.chunk_id}:semantic:{segment_index:03d}"
                        if len(segment_parts) == 1
                        else f"{chunk.chunk_id}:semantic:{segment_index:03d}:fixed:{part_index:03d}"
                    )
                    indexed_chunks.append(
                        self._chunk_with_strategy_metadata(
                            chunk,
                            chunk_id,
                            part,
                            "semantic",
                            len(indexed_chunks) + 1,
                            {
                                "source_chunk_id": chunk.chunk_id,
                                "semantic_segment_index": str(segment_index),
                                "chunk_part_index": str(part_index),
                            },
                        )
                    )

        return indexed_chunks

    def _split_fixed_size(self, text: str) -> list[str]:
        normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if not normalized:
            return []

        parts: list[str] = []
        remaining = normalized
        while len(remaining) > FIXED_SIZE_MAX_CHARS:
            split_at = max(
                remaining.rfind("\n", 0, FIXED_SIZE_MAX_CHARS + 1),
                remaining.rfind(" ", 0, FIXED_SIZE_MAX_CHARS + 1),
            )
            if split_at < FIXED_SIZE_MAX_CHARS // 2:
                split_at = FIXED_SIZE_MAX_CHARS

            part = remaining[:split_at].strip()
            if part:
                parts.append(part)
            remaining = remaining[split_at:].strip()

        if remaining:
            parts.append(remaining)

        return parts

    def _semantic_segments(self, text: str) -> list[str]:
        normalized = text.strip()
        if not normalized:
            return []

        segments = [
            "\n".join(line.strip() for line in segment.splitlines() if line.strip())
            for segment in normalized.split("\n\n")
        ]

        return [segment for segment in segments if segment]

    def _chunk_with_strategy_metadata(
        self,
        chunk: DocumentChunk,
        chunk_id: str,
        text: str,
        strategy: ChunkingStrategy,
        chunk_index: int,
        extra_metadata: dict[str, str],
    ) -> DocumentChunk:
        metadata = {
            **chunk.metadata,
            "chunking_strategy": strategy,
            "chunking_version": CHUNKING_VERSION,
            "chunk_index": str(chunk_index),
            "char_count": str(len(text)),
            "token_count": str(len(text.split())),
            "source_type": chunk.source_type,
            **extra_metadata,
        }
        if chunk.page_number is not None:
            metadata["page_number"] = str(chunk.page_number)

        return chunk.model_copy(
            update={
                "chunk_id": chunk_id,
                "text": text,
                "metadata": metadata,
            }
        )

    def _check_collection(self) -> None:
        collection = self.vector_store.get_collection()
        if not collection.exists:
            raise QdrantVectorStoreError(f"Qdrant collection '{self.vector_store.collection_name}' is missing.")

        if collection.vector_size != self.vector_store.vector_size:
            raise QdrantVectorStoreError(
                f"Qdrant collection '{self.vector_store.collection_name}' vector size is {collection.vector_size}; expected {self.vector_store.vector_size}."
            )

    def _point_from_chunk(self, document: DocumentMetadata, chunk: DocumentChunk) -> QdrantPoint:
        embedding = self.embedding_provider.embed(chunk.text)
        if embedding.dimension != self.vector_store.vector_size:
            raise ValueError(
                f"Embedding dimension is {embedding.dimension}; expected {self.vector_store.vector_size} for Qdrant collection '{self.vector_store.collection_name}'."
            )

        return QdrantPoint(
            point_id=self.point_id_for_chunk(document.document_id, chunk.chunk_id),
            vector=embedding.embedding,
            payload=self._payload_from_chunk(document, chunk, embedding.model),
        )

    def _payload_from_chunk(
        self,
        document: DocumentMetadata,
        chunk: DocumentChunk,
        embedding_model: str,
    ) -> dict[str, object]:
        payload = chunk.model_dump(mode="json")
        chunk_metadata = {
            str(key): str(value)
            for key, value in payload.get("metadata", {}).items()
        }
        ocr_provider = chunk_metadata.get("ocr_provider") or chunk_metadata.get("provider") or chunk.source_type
        metadata = {
            **chunk_metadata,
            "ocr_provider": str(ocr_provider),
            "indexing_provider": "vector",
            "vector_store": "qdrant",
            "qdrant_collection": self.vector_store.collection_name,
            "embedding_provider": self.embedding_provider.name,
            "embedding_model": embedding_model,
        }

        return {
            **payload,
            "filename": document.filename,
            "metadata": metadata,
            "ocr_provider": str(ocr_provider),
        }

    def _skipped_result(
        self,
        document_id: str,
        chunking_strategy: ChunkingStrategy,
        skipped_chunk_count: int,
        reason: str,
    ) -> VectorIndexingResult:
        return VectorIndexingResult(
            document_id=document_id,
            status="skipped",
            chunking_strategy=chunking_strategy,
            chunking_version=CHUNKING_VERSION,
            skipped_chunk_count=skipped_chunk_count,
            collection_name=self.vector_store.collection_name,
            vector_size=self.vector_store.vector_size,
            embedding_provider=self.embedding_provider.name,
            embedding_model=str(getattr(self.embedding_provider, "model", "unknown")),
            reason=reason,
        )

    def _failed_result(
        self,
        document_id: str,
        chunking_strategy: ChunkingStrategy,
        skipped_chunk_count: int,
        error: str,
    ) -> VectorIndexingResult:
        return VectorIndexingResult(
            document_id=document_id,
            status="failed",
            chunking_strategy=chunking_strategy,
            chunking_version=CHUNKING_VERSION,
            skipped_chunk_count=skipped_chunk_count,
            collection_name=self.vector_store.collection_name,
            vector_size=self.vector_store.vector_size,
            embedding_provider=self.embedding_provider.name,
            embedding_model=str(getattr(self.embedding_provider, "model", "unknown")),
            error=error,
        )
