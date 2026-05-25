from app.schemas.documents import BoundingBox, DocumentChunk, DocumentMetadata, DocumentStatus
from app.services.embedding import EmbeddingProviderError, EmbeddingResult
from app.services.vector_indexing import VectorIndexingService
from app.services.vector_store import QdrantCollectionStatus, QdrantPoint, QdrantVectorStoreError


class StubEmbeddingProvider:
    name = "ollama"
    model = "qwen3-embedding:0.6b"

    def __init__(self, vector_size: int = 3) -> None:
        self.vector_size = vector_size
        self.inputs: list[str] = []

    def embed(self, text: str) -> EmbeddingResult:
        self.inputs.append(text)
        return EmbeddingResult(
            embedding=[float(len(text))] * self.vector_size,
            model=self.model,
        )


class StubVectorStore:
    collection_name = "docurag_chunks_v1"

    def __init__(
        self,
        vector_size: int = 3,
        collection_size: int = 3,
        exists: bool = True,
        fail_on_upsert: bool = False,
    ) -> None:
        self.vector_size = vector_size
        self.collection_size = collection_size
        self.exists = exists
        self.fail_on_upsert = fail_on_upsert
        self.collection_checked = False
        self.points: list[QdrantPoint] = []

    def get_collection(self) -> QdrantCollectionStatus:
        self.collection_checked = True
        return QdrantCollectionStatus(
            collection_name=self.collection_name,
            exists=self.exists,
            vector_size=self.collection_size if self.exists else None,
            distance="Cosine" if self.exists else None,
        )

    def upsert_points(self, points: list[QdrantPoint]) -> None:
        if self.fail_on_upsert:
            raise QdrantVectorStoreError("Cannot connect to Qdrant")

        self.points = points


def make_document(chunks: list[DocumentChunk] | None = None) -> DocumentMetadata:
    return DocumentMetadata(
        document_id="doc-001",
        filename="invoice-a.txt",
        stored_filename="doc-001-invoice-a.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=chunks or [],
    )


def make_chunk(chunk_id: str = "chunk-001", text: str = "Payment terms are Net 15.") -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc-001",
        text=text,
        source="ocr_paddleocr",
        created_at="2026-05-20T00:00:00Z",
        page_number=2,
        bbox=BoundingBox(x_min=10, y_min=20, x_max=200, y_max=44),
        confidence=0.97,
        source_type="ocr_paddleocr",
        metadata={
            "origin": "ocr_line",
            "provider": "ocr_paddleocr",
            "line_index": "1",
        },
    )


def test_vector_indexing_service_upserts_chunk_payload() -> None:
    embedding_provider = StubEmbeddingProvider(vector_size=3)
    vector_store = StubVectorStore(vector_size=3)
    service = VectorIndexingService(embedding_provider, vector_store)
    document = make_document([make_chunk()])

    result = service.index_document(document)

    assert result.status == "completed"
    assert result.document_id == "doc-001"
    assert result.indexed_chunk_count == 1
    assert result.skipped_chunk_count == 0
    assert result.collection_name == "docurag_chunks_v1"
    assert result.vector_size == 3
    assert result.embedding_provider == "ollama"
    assert result.embedding_model == "qwen3-embedding:0.6b"
    assert vector_store.collection_checked is True
    assert embedding_provider.inputs == ["Payment terms are Net 15."]

    point = vector_store.points[0]
    assert point.point_id == service.point_id_for_chunk("doc-001", "chunk-001")
    assert result.point_ids == [point.point_id]
    assert point.vector == [25.0, 25.0, 25.0]
    assert point.payload["document_id"] == "doc-001"
    assert point.payload["filename"] == "invoice-a.txt"
    assert point.payload["chunk_id"] == "chunk-001"
    assert point.payload["text"] == "Payment terms are Net 15."
    assert point.payload["source"] == "ocr_paddleocr"
    assert point.payload["source_type"] == "ocr_paddleocr"
    assert point.payload["page_number"] == 2
    assert point.payload["bbox"] == {
        "x_min": 10.0,
        "y_min": 20.0,
        "x_max": 200.0,
        "y_max": 44.0,
    }
    assert point.payload["confidence"] == 0.97
    assert point.payload["created_at"] == "2026-05-20T00:00:00Z"
    assert point.payload["ocr_provider"] == "ocr_paddleocr"
    assert point.payload["metadata"] == {
        "origin": "ocr_line",
        "provider": "ocr_paddleocr",
        "line_index": "1",
        "ocr_provider": "ocr_paddleocr",
        "indexing_provider": "vector",
        "vector_store": "qdrant",
        "qdrant_collection": "docurag_chunks_v1",
        "embedding_provider": "ollama",
        "embedding_model": "qwen3-embedding:0.6b",
    }


def test_vector_indexing_service_preserves_text_upload_payload_metadata() -> None:
    embedding_provider = StubEmbeddingProvider(vector_size=3)
    vector_store = StubVectorStore(vector_size=3)
    service = VectorIndexingService(embedding_provider, vector_store)
    chunk = DocumentChunk(
        chunk_id="chunk-001",
        document_id="doc-001",
        text="Payment terms are Net 15.",
        source="text_upload",
        created_at="2026-05-20T00:00:00Z",
        source_type="text_upload",
        metadata={
            "origin": "uploaded_text",
            "content_source": "text_upload",
            "source_router": "text_upload",
        },
    )

    result = service.index_document(make_document([chunk]))

    assert result.status == "completed"
    point = vector_store.points[0]
    assert point.payload["source"] == "text_upload"
    assert point.payload["source_type"] == "text_upload"
    assert point.payload["ocr_provider"] == "text_upload"
    assert point.payload["metadata"] == {
        "origin": "uploaded_text",
        "content_source": "text_upload",
        "source_router": "text_upload",
        "ocr_provider": "text_upload",
        "indexing_provider": "vector",
        "vector_store": "qdrant",
        "qdrant_collection": "docurag_chunks_v1",
        "embedding_provider": "ollama",
        "embedding_model": "qwen3-embedding:0.6b",
    }


def test_vector_indexing_service_preserves_pdf_text_payload_metadata() -> None:
    embedding_provider = StubEmbeddingProvider(vector_size=3)
    vector_store = StubVectorStore(vector_size=3)
    service = VectorIndexingService(embedding_provider, vector_store)
    chunk = DocumentChunk(
        chunk_id="chunk-001",
        document_id="doc-001",
        text="Payment terms are Net 15.",
        source="pdf_text",
        created_at="2026-05-20T00:00:00Z",
        page_number=1,
        source_type="pdf_text",
        metadata={
            "origin": "pdf_text",
            "content_source": "pdf_text",
            "source_router": "pdf_text",
            "page_number": "1",
        },
    )

    result = service.index_document(make_document([chunk]))

    assert result.status == "completed"
    point = vector_store.points[0]
    assert point.payload["source"] == "pdf_text"
    assert point.payload["source_type"] == "pdf_text"
    assert point.payload["page_number"] == 1
    assert point.payload["bbox"] is None
    assert point.payload["confidence"] is None
    assert point.payload["ocr_provider"] == "pdf_text"
    assert point.payload["metadata"] == {
        "origin": "pdf_text",
        "content_source": "pdf_text",
        "source_router": "pdf_text",
        "page_number": "1",
        "ocr_provider": "pdf_text",
        "indexing_provider": "vector",
        "vector_store": "qdrant",
        "qdrant_collection": "docurag_chunks_v1",
        "embedding_provider": "ollama",
        "embedding_model": "qwen3-embedding:0.6b",
    }


def test_vector_indexing_service_uses_stable_point_ids() -> None:
    service = VectorIndexingService(StubEmbeddingProvider(), StubVectorStore())

    first = service.point_id_for_chunk("doc-001", "chunk-001")
    second = service.point_id_for_chunk("doc-001", "chunk-001")
    other = service.point_id_for_chunk("doc-001", "chunk-002")

    assert first == second
    assert first != other
    assert first == "1e077918-a4f5-5547-85d3-680d92ea9672"


def test_vector_indexing_service_skips_empty_chunks_without_external_calls() -> None:
    embedding_provider = StubEmbeddingProvider()
    vector_store = StubVectorStore()
    service = VectorIndexingService(embedding_provider, vector_store)

    result = service.index_document(make_document())

    assert result.status == "skipped"
    assert result.reason == "Document has no chunks to index."
    assert result.indexed_chunk_count == 0
    assert result.skipped_chunk_count == 0
    assert result.point_ids == []
    assert embedding_provider.inputs == []
    assert vector_store.collection_checked is False
    assert vector_store.points == []


def test_vector_indexing_service_reports_embedding_failure_without_upsert() -> None:
    class FailingEmbeddingProvider:
        name = "ollama"
        model = "qwen3-embedding:0.6b"

        def embed(self, text: str) -> EmbeddingResult:
            raise EmbeddingProviderError("Cannot connect to Ollama")

    vector_store = StubVectorStore()
    service = VectorIndexingService(FailingEmbeddingProvider(), vector_store)

    result = service.index_document(make_document([make_chunk()]))

    assert result.status == "failed"
    assert result.error == "Cannot connect to Ollama"
    assert result.indexed_chunk_count == 0
    assert result.point_ids == []
    assert vector_store.points == []


def test_vector_indexing_service_reports_qdrant_failure() -> None:
    service = VectorIndexingService(
        StubEmbeddingProvider(),
        StubVectorStore(fail_on_upsert=True),
    )

    result = service.index_document(make_document([make_chunk()]))

    assert result.status == "failed"
    assert result.error == "Cannot connect to Qdrant"
    assert result.point_ids == []


def test_vector_indexing_service_reports_collection_size_mismatch() -> None:
    vector_store = StubVectorStore(vector_size=3, collection_size=4)
    service = VectorIndexingService(StubEmbeddingProvider(), vector_store)

    result = service.index_document(make_document([make_chunk()]))

    assert result.status == "failed"
    assert result.error == (
        "Qdrant collection 'docurag_chunks_v1' vector size is 4; expected 3."
    )
    assert vector_store.points == []


def test_vector_indexing_service_reports_embedding_dimension_mismatch() -> None:
    service = VectorIndexingService(
        StubEmbeddingProvider(vector_size=4),
        StubVectorStore(vector_size=3, collection_size=3),
    )

    result = service.index_document(make_document([make_chunk()]))

    assert result.status == "failed"
    assert result.error == (
        "Embedding dimension is 4; expected 3 for Qdrant collection 'docurag_chunks_v1'."
    )
