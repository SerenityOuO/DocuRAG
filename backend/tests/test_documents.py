from datetime import datetime
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import get_document_storage, get_mock_ocr_provider, get_selected_ocr_provider
from app.core.config import get_settings
from app.main import app
from app.schemas.documents import BoundingBox, DocumentMetadata, OcrResult, OcrStatus, OcrTextLine, ProcessingJobType
from app.services.document_storage import DocumentStorage
from app.services import ocr as ocr_module
from app.services.ocr import MockOcrProvider, PaddleOcrProvider


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


def test_selected_ocr_default_provider_is_paddleocr() -> None:
    get_settings.cache_clear()

    try:
        provider = get_selected_ocr_provider()
    finally:
        get_settings.cache_clear()

    assert isinstance(provider, PaddleOcrProvider)


def test_selected_ocr_provider_can_be_overridden_to_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCURAG_OCR_PROVIDER", "mock")
    get_settings.cache_clear()

    try:
        provider = get_selected_ocr_provider()
    finally:
        get_settings.cache_clear()

    assert isinstance(provider, MockOcrProvider)


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
                lines=[OcrTextLine(text=f"Real OCR text for {document.filename}")],
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
    assert metadata[0]["chunks"][0]["page_number"] is None
    assert metadata[0]["chunks"][0]["bbox"] is None
    assert metadata[0]["chunks"][0]["confidence"] is None
    assert metadata[0]["chunks"][0]["source_type"] == "ocr_paddleocr"
    assert metadata[0]["chunks"][0]["metadata"] == {
        "origin": "ocr_line",
        "provider": "ocr_paddleocr",
    }


def test_run_selected_ocr_maps_real_trace_metadata_to_chunks(
    client: TestClient,
    tmp_path: Path,
) -> None:
    class TraceRealOcrProvider:
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
                status=OcrStatus.COMPLETED,
                text="Invoice total USD 120.00",
                extracted_fields={"provider": "paddleocr", "chunk_source": "ocr_paddleocr"},
                lines=[
                    OcrTextLine(
                        text="Invoice total USD 120.00",
                        page_number=2,
                        bbox=BoundingBox(x_min=12, y_min=24, x_max=220, y_max=48),
                        confidence=0.93,
                        metadata={"ocr_provider": "paddleocr", "line_index": "1"},
                    )
                ],
                updated_at=extracted_at,
            )

    app.dependency_overrides[get_selected_ocr_provider] = TraceRealOcrProvider
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("real-trace.png", b"fake image", "image/png")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/ocr")

    assert response.status_code == 200

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    chunk = metadata[0]["chunks"][0]
    assert chunk["text"] == "Invoice total USD 120.00"
    assert chunk["source"] == "ocr_paddleocr"
    assert chunk["page_number"] == 2
    assert chunk["bbox"] == {
        "x_min": 12.0,
        "y_min": 24.0,
        "x_max": 220.0,
        "y_max": 48.0,
    }
    assert chunk["confidence"] == 0.93
    assert chunk["source_type"] == "ocr_paddleocr"
    assert chunk["metadata"] == {
        "origin": "ocr_line",
        "provider": "ocr_paddleocr",
        "ocr_provider": "paddleocr",
        "line_index": "1",
    }


def test_paddleocr_provider_normalizes_raw_line_trace_metadata(tmp_path: Path) -> None:
    class StubPaddleEngine:
        def ocr(self, file_path: str, cls: bool = True):
            assert file_path.endswith("invoice.png")
            assert cls is True
            return [
                (
                    [[10, 20], [180, 20], [180, 44], [10, 44]],
                    ("Invoice number AUR-2026-051", 0.96),
                ),
                (
                    [[12, 60], [140, 60], [140, 82], [12, 82]],
                    ("Total USD 120.00", 0.91),
                ),
            ]

    file_path = tmp_path / "invoice.png"
    file_path.write_bytes(b"fake image")
    provider = PaddleOcrProvider()
    provider._engine = StubPaddleEngine()
    document = DocumentMetadata(
        document_id="doc-001",
        filename="invoice.png",
        stored_filename="doc-001-invoice.png",
        file_type="png",
        content_type="image/png",
        size=10,
        status="uploaded",
        created_at="2026-05-20T00:00:00Z",
    )

    result = provider.extract(document, file_path, datetime.fromisoformat("2026-05-20T00:00:01+00:00"))

    assert result.status == OcrStatus.COMPLETED
    assert result.text == "Invoice number AUR-2026-051\nTotal USD 120.00"
    assert result.extracted_fields["line_count"] == "2"
    assert result.extracted_fields["average_confidence"] == "0.9350"
    assert [line.page_number for line in result.lines] == [1, 1]
    assert result.lines[0].bbox == BoundingBox(x_min=10, y_min=20, x_max=180, y_max=44)
    assert result.lines[0].confidence == 0.96
    assert result.lines[0].metadata == {"ocr_provider": "paddleocr", "line_index": "1"}


def test_paddleocr_provider_reports_unsupported_python(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class UnsupportedVersionInfo:
        major = 3
        minor = 13
        micro = 0

        def __ge__(self, other: tuple[int, int]) -> bool:
            return (self.major, self.minor) >= other

    monkeypatch.setattr(ocr_module.sys, "version_info", UnsupportedVersionInfo())

    file_path = tmp_path / "invoice.png"
    file_path.write_bytes(b"fake image")
    provider = PaddleOcrProvider()
    document = DocumentMetadata(
        document_id="doc-001",
        filename="invoice.png",
        stored_filename="doc-001-invoice.png",
        file_type="png",
        content_type="image/png",
        size=10,
        status="uploaded",
        created_at="2026-05-20T00:00:00Z",
    )

    result = provider.extract(document, file_path, datetime.fromisoformat("2026-05-20T00:00:01+00:00"))

    assert result.status == OcrStatus.FAILED
    assert result.extracted_fields["provider"] == "paddleocr"
    assert result.extracted_fields["error_code"] == "paddleocr_python_unsupported"
    assert "Python 3.12" in result.extracted_fields["error"]
    assert 'py -3.12 -m pip install -e ".[dev,real-ocr]"' in result.extracted_fields["error"]


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
