import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import get_document_storage
from app.main import app
from app.services.document_storage import DocumentStorage


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_document_storage] = lambda: storage

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_upload_document_returns_uploaded_metadata(client: TestClient) -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["document_id"]
    assert "project_id" in body
    assert body["filename"] == "invoice.pdf"
    assert body["stored_filename"].endswith("-invoice.pdf")
    assert body["file_type"] == "pdf"
    assert body["content_type"] == "application/pdf"
    assert body["size"] == len(b"sample document")
    assert body["status"] == "uploaded"


def test_upload_document_saves_file_and_metadata(client: TestClient, tmp_path: Path) -> None:
    content = b"sample document"

    response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", content, "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    upload_path = tmp_path / "data" / "uploads" / body["stored_filename"]
    metadata_path = tmp_path / "data" / "documents.json"

    assert upload_path.read_bytes() == content
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata[0]["document_id"] == body["document_id"]
    assert metadata[0]["filename"] == "invoice.pdf"


def test_list_documents_returns_uploaded_documents_newest_first(client: TestClient) -> None:
    first_response = client.post(
        "/documents/upload",
        files={"file": ("first.pdf", b"first", "application/pdf")},
    )
    second_response = client.post(
        "/documents/upload",
        files={"file": ("second.pdf", b"second", "application/pdf")},
    )

    response = client.get("/documents")

    assert response.status_code == 200
    documents = response.json()["documents"]
    assert [document["document_id"] for document in documents] == [
        second_response.json()["document_id"],
        first_response.json()["document_id"],
    ]


def test_get_document_returns_uploaded_document(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id
    assert body["filename"] == "invoice.pdf"
    assert body["ocr"]["status"] == "pending"


def test_get_document_returns_404_for_unknown_document(client: TestClient) -> None:
    response = client.get("/documents/not-found")

    assert response.status_code == 404


def test_get_ocr_result_returns_pending_for_uploaded_document(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.get(f"/documents/{document_id}/ocr")

    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id
    assert body["status"] == "pending"
    assert body["text"] == ""
    assert body["extracted_fields"] == {}
    assert body["updated_at"] is None


def test_run_mock_ocr_saves_result_to_metadata(
    client: TestClient,
    tmp_path: Path,
) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/ocr/mock")

    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id
    assert body["status"] == "completed"
    assert "Mock OCR result for invoice.pdf" in body["text"]
    assert body["extracted_fields"] == {
        "filename": "invoice.pdf",
        "file_type": "pdf",
        "content_type": "application/pdf",
        "size_bytes": str(len(b"sample document")),
    }
    assert body["updated_at"]

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata[0]["status"] == "ready"
    assert metadata[0]["ocr"]["status"] == "completed"
    assert metadata[0]["ocr"]["text"] == body["text"]


def test_get_ocr_result_returns_saved_mock_result(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("receipt.txt", b"sample document", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]
    mock_response = client.post(f"/documents/{document_id}/ocr/mock")

    response = client.get(f"/documents/{document_id}/ocr")

    assert response.status_code == 200
    assert response.json() == mock_response.json()


def test_get_document_includes_saved_ocr_result(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("receipt.txt", b"sample document", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["ocr"]["status"] == "completed"
    assert body["ocr"]["extracted_fields"]["filename"] == "receipt.txt"


def test_run_mock_ocr_returns_404_for_unknown_document(client: TestClient) -> None:
    response = client.post("/documents/not-found/ocr/mock")

    assert response.status_code == 404


def test_get_ocr_result_returns_404_for_unknown_document(client: TestClient) -> None:
    response = client.get("/documents/not-found/ocr")

    assert response.status_code == 404


def test_unsafe_filename_cannot_escape_upload_directory(
    client: TestClient,
    tmp_path: Path,
) -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("../outside/..\\evil.pdf", b"unsafe", "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    upload_root = (tmp_path / "data" / "uploads").resolve()
    upload_path = (upload_root / body["stored_filename"]).resolve()

    assert body["filename"] == "evil.pdf"
    assert upload_path.is_file()
    assert upload_path.relative_to(upload_root)
    assert not (tmp_path / "outside").exists()
