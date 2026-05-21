import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import get_document_storage as get_documents_storage
from app.api.routes.rag import get_document_storage as get_rag_storage
from app.main import app
from app.services.document_storage import DocumentStorage


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
    assert body["citations"] == [
        {
            "document_id": document_id,
            "filename": "invoice.pdf",
            "chunk_id": f"{document_id}-chunk-001",
        }
    ]
    assert body["retrieved_chunks"][0]["document_id"] == document_id
    assert body["retrieved_chunks"][0]["chunk_id"] == f"{document_id}-chunk-001"
    assert body["retrieved_chunks"][0]["filename"] == "invoice.pdf"
    assert body["retrieved_chunks"][0]["score"] > 0
    assert "Mock OCR result for invoice.pdf" in body["retrieved_chunks"][0]["text"]


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


def test_rag_query_validates_request(client: TestClient) -> None:
    response = client.post(
        "/rag/query",
        json={"query": "", "top_k": 0},
    )

    assert response.status_code == 422
