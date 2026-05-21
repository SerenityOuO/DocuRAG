from datetime import datetime
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import get_document_storage, get_mock_ocr_provider, get_selected_ocr_provider
from app.main import app
from app.schemas.documents import DocumentMetadata, OcrResult, OcrStatus, ProcessingJobType
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
    assert body["processing"]["upload"] == "completed"
    assert body["processing"]["ocr"] == "pending"
    assert body["processing"]["indexing"] == "pending"
    assert body["processing"]["ready"] is False
    assert body["latest_job"]["job_type"] == "upload"
    assert body["latest_job"]["status"] == "completed"
    assert body["processing_jobs"][0]["job_type"] == "upload"


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
    assert metadata[0]["processing"]["upload"] == "completed"
    assert metadata[0]["processing"]["ocr"] == "pending"
    assert metadata[0]["processing"]["indexing"] == "pending"
    assert metadata[0]["latest_job"]["job_type"] == "upload"
    assert metadata[0]["processing_jobs"][0]["document_id"] == body["document_id"]


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
    assert metadata[0]["processing"]["ocr"] == "completed"
    assert metadata[0]["processing"]["indexing"] == "completed"
    assert metadata[0]["processing"]["ready"] is True
    assert [job["job_type"] for job in metadata[0]["processing_jobs"]] == [
        "upload",
        "ocr_mock",
        "local_indexing",
    ]
    assert metadata[0]["latest_job"]["job_type"] == "local_indexing"
    assert metadata[0]["latest_job"]["status"] == "completed"
    assert metadata[0]["ocr"]["status"] == "completed"
    assert metadata[0]["ocr"]["text"] == body["text"]
    assert metadata[0]["chunks"][0]["chunk_id"] == f"{document_id}-chunk-001"
    assert metadata[0]["chunks"][0]["document_id"] == document_id
    assert metadata[0]["chunks"][0]["source"] == "ocr_mock"
    assert metadata[0]["chunks"][0]["page_number"] is None
    assert metadata[0]["chunks"][0]["bbox"] is None
    assert metadata[0]["chunks"][0]["confidence"] is None
    assert metadata[0]["chunks"][0]["source_type"] == "ocr_mock"
    assert metadata[0]["chunks"][0]["metadata"] == {
        "origin": "ocr_text",
        "provider": "ocr_mock",
    }
    assert "Mock OCR result for invoice.pdf" in metadata[0]["chunks"][0]["text"]
    assert metadata[0]["chunks"][0]["created_at"]


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


def test_run_selected_ocr_uses_default_mock_provider(
    client: TestClient,
    tmp_path: Path,
) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("default-provider.txt", b"sample document", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/ocr")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert "Mock OCR result for default-provider.txt" in body["text"]

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert [job["job_type"] for job in metadata[0]["processing_jobs"]] == [
        "upload",
        "ocr_mock",
        "local_indexing",
    ]
    assert metadata[0]["chunks"][0]["source"] == "ocr_mock"


def test_run_selected_ocr_uses_real_provider_adapter(
    client: TestClient,
    tmp_path: Path,
) -> None:
    class StubRealOcrProvider:
        provider_name = "paddleocr"
        chunk_source = "ocr_paddleocr"
        job_type = ProcessingJobType.OCR_REAL

        def extract(
            self,
            document: DocumentMetadata,
            file_path: Path | None,
            extracted_at: datetime,
        ) -> OcrResult:
            assert file_path is not None
            return OcrResult(
                status=OcrStatus.COMPLETED,
                text=f"Real OCR text for {document.filename}",
                extracted_fields={"provider": "paddleocr"},
                updated_at=extracted_at,
            )

    app.dependency_overrides[get_selected_ocr_provider] = StubRealOcrProvider
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("real-provider.png", b"fake image", "image/png")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/ocr")

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Real OCR text for real-provider.png"
    assert body["extracted_fields"] == {"provider": "paddleocr"}

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata[0]["status"] == "ready"
    assert metadata[0]["processing"]["ocr"] == "completed"
    assert metadata[0]["processing"]["indexing"] == "completed"
    assert [job["job_type"] for job in metadata[0]["processing_jobs"]] == [
        "upload",
        "ocr_real",
        "local_indexing",
    ]
    assert metadata[0]["chunks"][0]["source"] == "ocr_paddleocr"
    assert metadata[0]["chunks"][0]["source_type"] == "ocr_paddleocr"
    assert metadata[0]["chunks"][0]["metadata"] == {
        "origin": "ocr_text",
        "provider": "ocr_paddleocr",
    }


def test_run_selected_ocr_returns_503_and_persists_real_failure(
    client: TestClient,
    tmp_path: Path,
) -> None:
    class FailingRealOcrProvider:
        provider_name = "paddleocr"
        chunk_source = "ocr_paddleocr"
        job_type = ProcessingJobType.OCR_REAL

        def extract(
            self,
            document: DocumentMetadata,
            file_path: Path | None,
            extracted_at: datetime,
        ) -> OcrResult:
            return OcrResult(
                status=OcrStatus.FAILED,
                text="",
                extracted_fields={
                    "provider": "paddleocr",
                    "error_code": "paddleocr_dependency_missing",
                    "error": "PaddleOCR dependency is not installed.",
                },
                updated_at=extracted_at,
            )

    app.dependency_overrides[get_selected_ocr_provider] = FailingRealOcrProvider
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("real-provider-failed.png", b"fake image", "image/png")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/ocr")

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "provider": "paddleocr",
        "error_code": "paddleocr_dependency_missing",
        "error": "PaddleOCR dependency is not installed.",
        "document_id": document_id,
    }

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata[0]["status"] == "failed"
    assert metadata[0]["processing"]["ocr"] == "failed"
    assert metadata[0]["processing"]["indexing"] == "pending"
    assert metadata[0]["processing"]["ready"] is False
    assert metadata[0]["processing"]["failed_reason"] == "PaddleOCR dependency is not installed."
    assert [job["job_type"] for job in metadata[0]["processing_jobs"]] == [
        "upload",
        "ocr_real",
    ]
    assert metadata[0]["latest_job"]["status"] == "failed"
    assert metadata[0]["latest_job"]["error_message"] == "PaddleOCR dependency is not installed."
    assert metadata[0]["chunks"] == []


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
    assert body["latest_job"]["job_type"] == "local_indexing"
    assert body["latest_job"]["status"] == "completed"
    assert body["ocr"]["status"] == "completed"
    assert body["ocr"]["extracted_fields"]["filename"] == "receipt.txt"
    assert body["chunks"][0]["source"] == "ocr_mock"


def test_run_mock_ocr_includes_uploaded_text_sample(client: TestClient) -> None:
    sample_text = b"Invoice number: AUR-2026-051\nPayment terms: Net 15"
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("demo-invoice.txt", sample_text, "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/ocr/mock")

    assert response.status_code == 200
    body = response.json()
    assert "Uploaded text content:" in body["text"]
    assert "Invoice number: AUR-2026-051" in body["text"]
    assert "Payment terms: Net 15" in body["text"]


def test_run_mock_ocr_uses_provider_output(client: TestClient, tmp_path: Path) -> None:
    class StubOcrProvider:
        chunk_source = "ocr_mock"
        job_type = ProcessingJobType.OCR_MOCK

        def extract(
            self,
            document: DocumentMetadata,
            file_path: Path | None,
            extracted_at: datetime,
        ) -> OcrResult:
            assert file_path is not None
            return OcrResult(
                status=OcrStatus.COMPLETED,
                text=f"Provider OCR text for {document.filename}",
                extracted_fields={"provider": "stub"},
                updated_at=extracted_at,
            )

    app.dependency_overrides[get_mock_ocr_provider] = StubOcrProvider
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("provider-check.txt", b"sample document", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/ocr/mock")

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Provider OCR text for provider-check.txt"
    assert body["extracted_fields"] == {"provider": "stub"}

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata[0]["ocr"]["text"] == body["text"]
    assert metadata[0]["chunks"][0]["text"] == body["text"]


def test_run_mock_ocr_persists_failed_processing_status(
    client: TestClient,
    tmp_path: Path,
) -> None:
    class FailingOcrProvider:
        chunk_source = "ocr_mock"
        job_type = ProcessingJobType.OCR_MOCK

        def extract(
            self,
            document: DocumentMetadata,
            file_path: Path | None,
            extracted_at: datetime,
        ) -> OcrResult:
            return OcrResult(
                status=OcrStatus.FAILED,
                text="",
                extracted_fields={"error": "provider failed"},
                updated_at=extracted_at,
            )

    app.dependency_overrides[get_mock_ocr_provider] = FailingOcrProvider
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("failed-ocr.txt", b"sample document", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/ocr/mock")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata[0]["status"] == "failed"
    assert metadata[0]["processing"]["ocr"] == "failed"
    assert metadata[0]["processing"]["indexing"] == "pending"
    assert metadata[0]["processing"]["ready"] is False
    assert metadata[0]["processing"]["failed_reason"] == "provider failed"
    assert [job["job_type"] for job in metadata[0]["processing_jobs"]] == [
        "upload",
        "ocr_mock",
    ]
    assert metadata[0]["latest_job"]["status"] == "failed"
    assert metadata[0]["latest_job"]["error_message"] == "provider failed"
    assert metadata[0]["chunks"] == []


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
