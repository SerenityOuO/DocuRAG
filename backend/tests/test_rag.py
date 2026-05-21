import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import get_document_storage as get_documents_storage
from app.api.routes.rag import get_document_storage as get_rag_storage
from app.api.routes.rag import get_rag_provider
from app.main import app
from app.schemas.documents import DocumentChunk, DocumentMetadata, DocumentStatus
from app.schemas.rag import RagCitation, RagQueryResponse
from app.services.document_storage import DocumentStorage
from app.services.rag import KeywordRagProvider


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_documents_storage] = lambda: storage
    app.dependency_overrides[get_rag_storage] = lambda: storage

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


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
    assert "Local OCR mock chunks matched the query" in body["answer"]
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
    assert "No OCR mock chunks matched query: invoice" in body["answer"]
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
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(
        "/rag/query",
        json={"query": "payment due date Net 15", "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"][0]["filename"] == "mock-invoice-aurora.txt"
    assert "AUR-2026-051" in body["retrieved_chunks"][0]["text"]
    assert "Payment terms: Net 15" in body["retrieved_chunks"][0]["text"]


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
                    source="ocr_mock",
                    created_at="2026-05-20T00:00:00Z",
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

    assert response.answer.startswith("Local OCR mock chunks matched the query")
    assert response.citations == [
        RagCitation(
            document_id="doc-001",
            filename="invoice-a.txt",
            chunk_id="doc-001-chunk-001",
            page_number=None,
            bbox=None,
            confidence=None,
            source_type="ocr_mock",
            trace_metadata={"source": "ocr_mock"},
        )
    ]
    assert len(response.retrieved_chunks) == 1
    assert response.retrieved_chunks[0].chunk_id == "doc-001-chunk-001"
    assert response.retrieved_chunks[0].score == 3


def test_keyword_rag_provider_returns_empty_result() -> None:
    response = KeywordRagProvider().query("missing", 3, [])

    assert "No OCR mock chunks matched query: missing" in response.answer
    assert response.citations == []
    assert response.retrieved_chunks == []


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
