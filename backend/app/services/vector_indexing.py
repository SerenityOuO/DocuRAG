from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from app.schemas.documents import DocumentChunk, DocumentMetadata
from app.services.embedding import EmbeddingProvider, EmbeddingProviderError
from app.services.vector_store import QdrantPoint, QdrantVectorStore, QdrantVectorStoreError


VectorIndexingStatus = Literal["completed", "skipped", "failed"]


@dataclass(frozen=True)
class VectorIndexingResult:
    document_id: str
    status: VectorIndexingStatus
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

    def index_document(self, document: DocumentMetadata) -> VectorIndexingResult:
        chunks = [chunk for chunk in document.chunks if chunk.text.strip()]
        skipped_chunk_count = len(document.chunks) - len(chunks)

        if not chunks:
            return self._skipped_result(
                document.document_id,
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
                skipped_chunk_count=skipped_chunk_count,
                error=str(exc),
            )

        return VectorIndexingResult(
            document_id=document.document_id,
            status="completed",
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
        skipped_chunk_count: int,
        reason: str,
    ) -> VectorIndexingResult:
        return VectorIndexingResult(
            document_id=document_id,
            status="skipped",
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
        skipped_chunk_count: int,
        error: str,
    ) -> VectorIndexingResult:
        return VectorIndexingResult(
            document_id=document_id,
            status="failed",
            skipped_chunk_count=skipped_chunk_count,
            collection_name=self.vector_store.collection_name,
            vector_size=self.vector_store.vector_size,
            embedding_provider=self.embedding_provider.name,
            embedding_model=str(getattr(self.embedding_provider, "model", "unknown")),
            error=error,
        )
