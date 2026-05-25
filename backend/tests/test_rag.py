import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import get_document_storage as get_documents_storage
from app.api.routes.rag import get_document_storage as get_rag_storage
from app.api.routes.rag import get_rag_provider
from app.core.config import get_settings
from app.main import app
from app.schemas.documents import BoundingBox, DocumentChunk, DocumentMetadata, DocumentStatus
from app.schemas.rag import RagCitation, RagQueryResponse
from app.services.embedding import EmbeddingProviderError, EmbeddingResult
from app.services.document_storage import DocumentStorage
from app.services.llm import LlmGeneration, LlmProviderError
from app.services.rag import (
    HybridRagProvider,
    HybridRerankRagProvider,
    KeywordRagProvider,
    VectorRagProvider,
)
from app.services.vector_store import (
    QdrantCollectionStatus,
    QdrantPoint,
    QdrantSearchResult,
    QdrantVectorStoreError,
)


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_documents_storage] = lambda: storage
    app.dependency_overrides[get_rag_storage] = lambda: storage
    app.dependency_overrides[get_rag_provider] = lambda: KeywordRagProvider()

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def _pdf_bytes(text_lines: list[str]) -> bytes:
    text_commands = ["BT", "/F1 12 Tf", "72 720 Td"]
    for line_index, line in enumerate(text_lines):
        if line_index > 0:
            text_commands.append("0 -16 Td")

        safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        text_commands.append(f"({safe_line}) Tj")

    text_commands.append("ET")
    content_stream = "\n".join(text_commands)
    objects = [
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            "3 0 obj\n"
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\n"
            "endobj\n"
        ),
        "4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        (
            "5 0 obj\n"
            f"<< /Length {len(content_stream.encode('latin-1'))} >>\n"
            "stream\n"
            f"{content_stream}\n"
            "endstream\n"
            "endobj\n"
        ),
    ]
    content = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(content.encode("latin-1")))
        content += obj

    xref_offset = len(content.encode("latin-1"))
    content += "xref\n0 6\n0000000000 65535 f \n"
    content += "".join(f"{offset:010d} 00000 n \n" for offset in offsets[1:])
    content += "trailer\n<< /Size 6 /Root 1 0 R >>\n"
    content += f"startxref\n{xref_offset}\n%%EOF\n"
    return content.encode("latin-1")


def test_rag_query_returns_answer_citations_and_retrieved_chunks(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample invoice", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(
        "/rag/query",
        json={"query": "invoice", "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert "Local OCR chunks matched the query" in body["answer"]
    assert len(body["citations"]) == 1
    citation = body["citations"][0]
    assert citation["document_id"] == document_id
    assert citation["filename"] == "invoice.pdf"
    assert citation["chunk_id"] == f"{document_id}-chunk-001"
    assert citation["page_number"] is None
    assert citation["bbox"] is None
    assert citation["confidence"] is None
    assert citation["source_type"] == "ocr_mock"
    assert citation["trace_metadata"] == {
        "origin": "ocr_text",
        "provider": "ocr_mock",
        "source": "ocr_mock",
    }
    assert body["retrieved_chunks"][0]["document_id"] == document_id
    assert body["retrieved_chunks"][0]["chunk_id"] == f"{document_id}-chunk-001"
    assert body["retrieved_chunks"][0]["filename"] == "invoice.pdf"
    assert body["retrieved_chunks"][0]["score"] > 0
    assert "Mock OCR result for invoice.pdf" in body["retrieved_chunks"][0]["text"]
    assert body["retrieved_chunks"][0]["page_number"] is None
    assert body["retrieved_chunks"][0]["confidence"] is None
    assert body["retrieved_chunks"][0]["source_type"] == "ocr_mock"
    assert body["retrieved_chunks"][0]["metadata"] == {
        "origin": "ocr_text",
        "provider": "ocr_mock",
    }


def test_rag_query_returns_empty_result_before_ocr(client: TestClient) -> None:
    client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample invoice", "application/pdf")},
    )

    response = client.post(
        "/rag/query",
        json={"query": "invoice", "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert "No OCR chunks matched query: invoice" in body["answer"]
    assert body["citations"] == []
    assert body["retrieved_chunks"] == []


def test_rag_query_retrieves_uploaded_text_sample_content(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "mock-invoice-aurora.txt",
                b"Invoice number: AUR-2026-051\nDue date: 2026-06-15\nPayment terms: Net 15",
                "text/plain",
            )
        },
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(
        "/rag/query",
        json={"query": "payment due date Net 15", "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"][0]["filename"] == "mock-invoice-aurora.txt"
    assert body["citations"][0]["source_type"] == "text_upload"
    assert body["citations"][0]["trace_metadata"]["origin"] == "uploaded_text"
    assert "AUR-2026-051" in body["retrieved_chunks"][0]["text"]
    assert "Payment terms: Net 15" in body["retrieved_chunks"][0]["text"]
    assert body["retrieved_chunks"][0]["source_type"] == "text_upload"


def test_rag_query_retrieves_text_native_pdf_chunks(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "invoice.pdf",
                _pdf_bytes(
                    [
                        "Invoice number: AUR-2026-051",
                        "Payment terms: Net 15",
                        "Total: USD 1248.50",
                    ]
                ),
                "application/pdf",
            )
        },
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(
        "/rag/query",
        json={"query": "payment terms Net 15", "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"][0]["document_id"] == document_id
    assert body["citations"][0]["filename"] == "invoice.pdf"
    assert body["citations"][0]["source_type"] == "pdf_text"
    assert body["citations"][0]["page_number"] == 1
    assert body["citations"][0]["bbox"] is None
    assert body["citations"][0]["confidence"] is None
    assert body["citations"][0]["trace_metadata"]["origin"] == "pdf_text"
    assert body["retrieved_chunks"][0]["source_type"] == "pdf_text"
    assert body["retrieved_chunks"][0]["page_number"] == 1
    assert "AUR-2026-051" in body["retrieved_chunks"][0]["text"]


def test_keyword_rag_provider_retrieves_english_chunk_from_chinese_payment_query() -> None:
    document = DocumentMetadata(
        document_id="doc-001",
        filename="mock-invoice-aurora.txt",
        stored_filename="doc-001-mock-invoice-aurora.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="chunk-001",
                document_id="doc-001",
                text=(
                    "Invoice number: AUR-2026-051\n"
                    "Due date: 2026-06-15\n"
                    "Payment terms: Net 15"
                ),
                source="ocr_mock",
                created_at="2026-05-20T00:00:00Z",
                source_type="ocr_mock",
                metadata={"origin": "ocr_text", "provider": "ocr_mock"},
            )
        ],
    )

    response = KeywordRagProvider().query("付款期限是什麼？", 3, [document])

    assert response.citations[0].filename == "mock-invoice-aurora.txt"
    assert response.retrieved_chunks[0].chunk_id == "chunk-001"
    assert response.retrieved_chunks[0].score >= 3
    assert "Payment terms: Net 15" in response.retrieved_chunks[0].text


def test_keyword_rag_provider_sends_chinese_alias_match_to_llm() -> None:
    class StubLlmProvider:
        name = "ollama"

        def __init__(self) -> None:
            self.prompt = ""

        def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
            self.prompt = prompt
            return LlmGeneration(
                text="付款期限是 Net 15，支援 chunk-001。",
                model="qwen3.5:4b",
            )

    llm_provider = StubLlmProvider()
    document = DocumentMetadata(
        document_id="doc-001",
        filename="mock-invoice-aurora.txt",
        stored_filename="doc-001-mock-invoice-aurora.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="chunk-001",
                document_id="doc-001",
                text="Payment terms: Net 15",
                source="ocr_mock",
                created_at="2026-05-20T00:00:00Z",
            )
        ],
    )

    response = KeywordRagProvider(llm_provider=llm_provider).query("付款期限是什麼？", 3, [document])

    assert response.answer == "付款期限是 Net 15，支援 chunk-001。"
    assert "付款期限是什麼？" in llm_provider.prompt
    assert "Payment terms: Net 15" in llm_provider.prompt
    assert response.citations[0].trace_metadata["llm_generation_status"] == "completed"


def test_keyword_rag_provider_scores_sorts_and_limits_results() -> None:
    documents = [
        DocumentMetadata(
            document_id="doc-001",
            filename="invoice-a.txt",
            stored_filename="doc-001-invoice-a.txt",
            file_type="txt",
            content_type="text/plain",
            size=100,
            status=DocumentStatus.READY,
            created_at="2026-05-20T00:00:00Z",
            chunks=[
                DocumentChunk(
                    chunk_id="doc-001-chunk-001",
                    document_id="doc-001",
                    text="invoice invoice payment terms net 15",
                    source="ocr_paddleocr",
                    created_at="2026-05-20T00:00:00Z",
                    page_number=1,
                    bbox=BoundingBox(x_min=10, y_min=20, x_max=200, y_max=44),
                    confidence=0.97,
                    source_type="ocr_paddleocr",
                    metadata={
                        "origin": "ocr_line",
                        "provider": "ocr_paddleocr",
                        "line_index": "1",
                    },
                ),
                DocumentChunk(
                    chunk_id="doc-001-chunk-002",
                    document_id="doc-001",
                    text="invoice support contract",
                    source="ocr_mock",
                    created_at="2026-05-21T00:00:00Z",
                ),
            ],
        )
    ]

    response = KeywordRagProvider().query("invoice payment", 1, documents)

    assert response.answer.startswith("Local OCR chunks matched the query")
    assert response.citations == [
        RagCitation(
            document_id="doc-001",
            filename="invoice-a.txt",
            chunk_id="doc-001-chunk-001",
            page_number=1,
            bbox=BoundingBox(x_min=10, y_min=20, x_max=200, y_max=44),
            confidence=0.97,
            source_type="ocr_paddleocr",
            trace_metadata={
                "source": "ocr_paddleocr",
                "origin": "ocr_line",
                "provider": "ocr_paddleocr",
                "line_index": "1",
            },
        )
    ]
    assert len(response.retrieved_chunks) == 1
    assert response.retrieved_chunks[0].chunk_id == "doc-001-chunk-001"
    assert response.retrieved_chunks[0].score == 3


def test_keyword_rag_provider_returns_empty_result() -> None:
    response = KeywordRagProvider().query("missing", 3, [])

    assert "No OCR chunks matched query: missing" in response.answer
    assert response.citations == []
    assert response.retrieved_chunks == []


def test_keyword_rag_provider_uses_llm_generation_with_retrieved_chunks() -> None:
    class StubLlmProvider:
        name = "ollama"

        def __init__(self) -> None:
            self.prompt = ""
            self.system = ""

        def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
            self.prompt = prompt
            self.system = system or ""
            return LlmGeneration(
                text="Generated answer from retrieved chunks.",
                model="qwen3.5:4b",
                prompt_tokens=42,
                completion_tokens=9,
                total_duration_ms=123.45,
                load_duration_ms=10.0,
            )

    llm_provider = StubLlmProvider()
    document = DocumentMetadata(
        document_id="doc-001",
        filename="invoice-a.txt",
        stored_filename="doc-001-invoice-a.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="chunk-001",
                document_id="doc-001",
                text="Invoice total is USD 42.00.",
                source="ocr_paddleocr",
                created_at="2026-05-20T00:00:00Z",
                page_number=1,
                source_type="ocr_paddleocr",
                metadata={"origin": "ocr_line", "provider": "ocr_paddleocr"},
            )
        ],
    )

    response = KeywordRagProvider(llm_provider=llm_provider).query("What is the invoice total?", 3, [document])

    assert response.answer == "Generated answer from retrieved chunks."
    assert "Use only the retrieved chunks" in llm_provider.prompt
    assert "What is the invoice total?" in llm_provider.prompt
    assert "chunk_id=chunk-001" in llm_provider.prompt
    assert "Invoice total is USD 42.00." in llm_provider.prompt
    assert "using only the supplied retrieved OCR chunks" in llm_provider.system
    assert response.retrieved_chunks[0].chunk_id == "chunk-001"
    assert response.citations[0].chunk_id == "chunk-001"
    assert response.citations[0].trace_metadata == {
        "source": "ocr_paddleocr",
        "origin": "ocr_line",
        "provider": "ocr_paddleocr",
        "llm_generation_status": "completed",
        "llm_provider": "ollama",
        "llm_model": "qwen3.5:4b",
        "llm_prompt_source": "retrieved_chunks",
        "llm_prompt_chunk_count": "1",
        "llm_prompt_tokens": "42",
        "llm_completion_tokens": "9",
        "llm_total_duration_ms": "123.45",
        "llm_load_duration_ms": "10.00",
        "llm_generation_latency_ms": response.citations[0].trace_metadata["llm_generation_latency_ms"],
    }


def test_keyword_rag_provider_falls_back_when_llm_generation_fails() -> None:
    class FailingLlmProvider:
        name = "ollama"
        model = "qwen3.5:4b"

        def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
            raise LlmProviderError("Cannot connect to Ollama")

    document = DocumentMetadata(
        document_id="doc-001",
        filename="invoice-a.txt",
        stored_filename="doc-001-invoice-a.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="chunk-001",
                document_id="doc-001",
                text="Invoice total is USD 42.00.",
                source="ocr_paddleocr",
                created_at="2026-05-20T00:00:00Z",
            )
        ],
    )

    response = KeywordRagProvider(llm_provider=FailingLlmProvider()).query("invoice total", 3, [document])

    assert "Local OCR chunks matched the query" in response.answer
    assert "LLM generation unavailable; returning retrieved OCR chunks only" in response.answer
    assert "Cannot connect to Ollama" in response.answer
    assert response.citations[0].trace_metadata["llm_generation_status"] == "failed"
    assert response.citations[0].trace_metadata["llm_provider"] == "ollama"
    assert response.citations[0].trace_metadata["llm_model"] == "qwen3.5:4b"
    assert response.citations[0].trace_metadata["llm_error"] == "Cannot connect to Ollama"


def test_vector_rag_provider_uses_embedding_and_qdrant_results() -> None:
    class StubEmbeddingProvider:
        name = "ollama"
        model = "qwen3-embedding:0.6b"

        def __init__(self) -> None:
            self.inputs: list[str] = []

        def embed(self, text: str) -> EmbeddingResult:
            self.inputs.append(text)
            return EmbeddingResult(embedding=[float(len(text)), 1.0], model=self.model)

    class StubVectorStore:
        collection_name = "docurag_chunks_v1"
        vector_size = 1024

        def __init__(self, payload: dict[str, object]) -> None:
            self.payload = payload
            self.collection_checked = False
            self.upsert_called = False

        def get_collection(self) -> QdrantCollectionStatus:
            self.collection_checked = True
            return QdrantCollectionStatus(
                collection_name=self.collection_name,
                exists=True,
                vector_size=1024,
                distance="Cosine",
            )

        def upsert_points(self, points: list[QdrantPoint]) -> None:
            self.upsert_called = True

        def search(self, vector: list[float], limit: int) -> list[QdrantSearchResult]:
            assert vector == [float(len("payment due date Net 15")), 1.0]
            assert limit == 3
            return [
                QdrantSearchResult(
                    point_id="point-001",
                    score=0.88,
                    payload=self.payload,
                )
            ]

    document = DocumentMetadata(
        document_id="doc-001",
        filename="invoice-a.txt",
        stored_filename="doc-001-invoice-a.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="chunk-001",
                document_id="doc-001",
                text="Payment terms are Net 15.",
                source="ocr_mock",
                created_at="2026-05-20T00:00:00Z",
                source_type="ocr_mock",
                metadata={"origin": "ocr_text", "provider": "ocr_mock"},
            )
        ],
    )
    embedding_provider = StubEmbeddingProvider()
    payload = {
        **document.chunks[0].model_dump(mode="json"),
        "filename": document.filename,
        "metadata": {
            **document.chunks[0].metadata,
            "indexing_provider": "vector",
            "vector_store": "qdrant",
            "qdrant_collection": "docurag_chunks_v1",
            "embedding_provider": "ollama",
            "embedding_model": "qwen3-embedding:0.6b",
        },
    }
    vector_store = StubVectorStore(payload)
    provider = VectorRagProvider(
        keyword_provider=KeywordRagProvider(),
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    response = provider.query("payment due date Net 15", 3, [document])

    assert vector_store.collection_checked is True
    assert vector_store.upsert_called is False
    assert embedding_provider.inputs == ["payment due date Net 15"]
    assert response.answer.startswith("Local OCR chunks matched the query")
    assert response.retrieved_chunks[0].score == 0.88
    assert response.retrieved_chunks[0].metadata["retrieval_provider"] == "vector"
    assert response.retrieved_chunks[0].metadata["vector_retrieval_status"] == "completed"
    assert response.retrieved_chunks[0].metadata["embedding_model"] == "qwen3-embedding:0.6b"
    assert response.citations[0].trace_metadata["retrieval_provider"] == "vector"
    assert response.citations[0].trace_metadata["vector_store"] == "qdrant"
    assert response.citations[0].trace_metadata["vector_score"] == "0.880000"


def test_vector_rag_provider_falls_back_to_keyword_when_embedding_fails() -> None:
    class FailingEmbeddingProvider:
        name = "ollama"
        model = "qwen3-embedding:0.6b"

        def embed(self, text: str) -> EmbeddingResult:
            raise EmbeddingProviderError("Cannot connect to Ollama")

    class StubVectorStore:
        collection_name = "docurag_chunks_v1"
        vector_size = 1024

        def get_collection(self) -> QdrantCollectionStatus:
            return QdrantCollectionStatus(
                collection_name=self.collection_name,
                exists=True,
                vector_size=1024,
                distance="Cosine",
            )

        def upsert_points(self, points: list[QdrantPoint]) -> None:
            pass

        def search(self, vector: list[float], limit: int) -> list[QdrantSearchResult]:
            return []

    document = DocumentMetadata(
        document_id="doc-001",
        filename="invoice-a.txt",
        stored_filename="doc-001-invoice-a.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="chunk-001",
                document_id="doc-001",
                text="Payment terms are Net 15.",
                source="ocr_mock",
                created_at="2026-05-20T00:00:00Z",
                source_type="ocr_mock",
                metadata={"origin": "ocr_text", "provider": "ocr_mock"},
            )
        ],
    )
    provider = VectorRagProvider(
        keyword_provider=KeywordRagProvider(),
        embedding_provider=FailingEmbeddingProvider(),
        vector_store=StubVectorStore(),
    )

    response = provider.query("payment terms", 3, [document])

    assert "Local OCR chunks matched the query" in response.answer
    assert "Vector retrieval unavailable; fallback to keyword retrieval" in response.answer
    assert response.citations[0].trace_metadata["retrieval_provider"] == "keyword"
    assert response.citations[0].trace_metadata["vector_retrieval_status"] == "failed"
    assert response.citations[0].trace_metadata["vector_retrieval_error"] == "Cannot connect to Ollama"
    assert response.retrieved_chunks[0].metadata["retrieval_provider"] == "keyword"


def test_vector_rag_provider_falls_back_to_keyword_when_qdrant_fails() -> None:
    class StubEmbeddingProvider:
        name = "ollama"
        model = "qwen3-embedding:0.6b"

        def embed(self, text: str) -> EmbeddingResult:
            return EmbeddingResult(embedding=[1.0, 2.0], model=self.model)

    class FailingVectorStore:
        collection_name = "docurag_chunks_v1"

        def get_collection(self) -> QdrantCollectionStatus:
            raise QdrantVectorStoreError("Cannot connect to Qdrant")

        def upsert_points(self, points: list[QdrantPoint]) -> None:
            pass

        def search(self, vector: list[float], limit: int) -> list[QdrantSearchResult]:
            return []

    document = DocumentMetadata(
        document_id="doc-001",
        filename="invoice-a.txt",
        stored_filename="doc-001-invoice-a.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="chunk-001",
                document_id="doc-001",
                text="Payment terms are Net 15.",
                source="ocr_mock",
                created_at="2026-05-20T00:00:00Z",
            )
        ],
    )
    provider = VectorRagProvider(
        keyword_provider=KeywordRagProvider(),
        embedding_provider=StubEmbeddingProvider(),
        vector_store=FailingVectorStore(),
    )

    response = provider.query("payment terms", 3, [document])

    assert "Vector retrieval unavailable; fallback to keyword retrieval" in response.answer
    assert response.citations[0].trace_metadata["vector_retrieval_error"] == "Cannot connect to Qdrant"


def test_vector_rag_provider_falls_back_to_keyword_when_collection_missing() -> None:
    class StubEmbeddingProvider:
        name = "ollama"
        model = "qwen3-embedding:0.6b"

        def embed(self, text: str) -> EmbeddingResult:
            return EmbeddingResult(embedding=[1.0, 2.0], model=self.model)

    class MissingCollectionVectorStore:
        collection_name = "docurag_chunks_v1"
        vector_size = 1024

        def get_collection(self) -> QdrantCollectionStatus:
            return QdrantCollectionStatus(
                collection_name=self.collection_name,
                exists=False,
            )

        def upsert_points(self, points: list[QdrantPoint]) -> None:
            raise AssertionError("Vector fallback should not upsert when collection is missing.")

        def search(self, vector: list[float], limit: int) -> list[QdrantSearchResult]:
            raise AssertionError("Vector fallback should not search when collection is missing.")

    document = DocumentMetadata(
        document_id="doc-001",
        filename="invoice-a.txt",
        stored_filename="doc-001-invoice-a.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at="2026-05-20T00:00:00Z",
        chunks=[
            DocumentChunk(
                chunk_id="chunk-001",
                document_id="doc-001",
                text="Payment terms are Net 15.",
                source="ocr_mock",
                created_at="2026-05-20T00:00:00Z",
            )
        ],
    )
    provider = VectorRagProvider(
        keyword_provider=KeywordRagProvider(),
        embedding_provider=StubEmbeddingProvider(),
        vector_store=MissingCollectionVectorStore(),
    )

    response = provider.query("payment terms", 3, [document])

    assert "Vector retrieval unavailable; fallback to keyword retrieval" in response.answer
    assert response.citations[0].trace_metadata["retrieval_provider"] == "keyword"
    assert response.citations[0].trace_metadata["vector_retrieval_status"] == "failed"
    assert response.citations[0].trace_metadata["vector_retrieval_error"] == (
        "Qdrant collection 'docurag_chunks_v1' is missing."
    )


def test_get_rag_provider_enables_ollama_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCURAG_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("DOCURAG_LLM_MODEL", "qwen3.5:4b")
    monkeypatch.setenv("DOCURAG_LLM_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("DOCURAG_RAG_RETRIEVAL_PROVIDER", "keyword")
    get_settings.cache_clear()

    try:
        provider = get_rag_provider()
    finally:
        get_settings.cache_clear()

    assert isinstance(provider, KeywordRagProvider)
    assert provider.llm_provider is not None
    assert provider.llm_provider.name == "ollama"


def test_get_rag_provider_enables_default_ollama_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DOCURAG_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("DOCURAG_RAG_RETRIEVAL_PROVIDER", raising=False)
    monkeypatch.delenv("DOCURAG_EMBEDDING_PROVIDER", raising=False)
    monkeypatch.delenv("DOCURAG_RERANK_PROVIDER", raising=False)
    get_settings.cache_clear()

    try:
        provider = get_rag_provider()
    finally:
        get_settings.cache_clear()

    assert isinstance(provider, HybridRerankRagProvider)
    assert provider.rerank_service.provider.name == "fastembed"
    assert isinstance(provider.hybrid_provider, HybridRagProvider)
    assert provider.hybrid_provider.vector_provider.embedding_provider.name == "ollama"
    assert provider.hybrid_provider.keyword_provider.llm_provider is not None
    assert provider.hybrid_provider.keyword_provider.llm_provider.name == "ollama"


def test_get_rag_provider_enables_vector_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCURAG_RAG_RETRIEVAL_PROVIDER", "vector")
    monkeypatch.setenv("DOCURAG_EMBEDDING_PROVIDER", "ollama")
    monkeypatch.setenv("DOCURAG_QDRANT_URL", "http://127.0.0.1:6333")
    get_settings.cache_clear()

    try:
        provider = get_rag_provider()
    finally:
        get_settings.cache_clear()

    assert isinstance(provider, VectorRagProvider)
    assert provider.embedding_provider.name == "ollama"
    assert provider.vector_store.collection_name == "docurag_chunks_v1"


def test_rag_query_backfills_chunks_from_existing_ocr_text(
    client: TestClient,
    tmp_path: Path,
) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("legacy-invoice.pdf", b"sample invoice", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata[0]["chunks"] = []
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    response = client.post(
        "/rag/query",
        json={"query": "legacy invoice", "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"][0]["filename"] == "legacy-invoice.pdf"
    assert body["retrieved_chunks"][0]["chunk_id"] == f"{document_id}-chunk-001"

    saved_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert saved_metadata[0]["chunks"][0]["chunk_id"] == f"{document_id}-chunk-001"
    assert saved_metadata[0]["processing"]["indexing"] == "completed"
    assert saved_metadata[0]["processing"]["ready"] is True
    assert saved_metadata[0]["latest_job"]["job_type"] == "local_indexing"
    assert saved_metadata[0]["latest_job"]["status"] == "completed"


def test_rag_query_uses_provider_response(client: TestClient) -> None:
    class StubRagProvider:
        def query(
            self,
            query: str,
            top_k: int,
            documents: list[DocumentMetadata],
        ) -> RagQueryResponse:
            assert query == "invoice"
            assert top_k == 2
            assert len(documents) == 1
            return RagQueryResponse(
                answer="Provider answer",
                citations=[],
                retrieved_chunks=[],
            )

    app.dependency_overrides[get_rag_provider] = StubRagProvider
    client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample invoice", "application/pdf")},
    )

    response = client.post(
        "/rag/query",
        json={"query": "invoice", "top_k": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Provider answer",
        "citations": [],
        "retrieved_chunks": [],
    }


def test_rag_query_validates_request(client: TestClient) -> None:
    response = client.post(
        "/rag/query",
        json={"query": "", "top_k": 0},
    )

    assert response.status_code == 422
