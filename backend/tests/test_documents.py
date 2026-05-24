from datetime import datetime
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import (
    _reset_selected_ocr_provider_cache,
    get_document_storage,
    get_document_parser,
    get_mock_ocr_provider,
    get_selected_ocr_provider,
    get_vector_indexing_service,
    preload_selected_ocr_provider,
)
from app.core.config import get_settings
from app.main import app
from app.schemas.documents import BoundingBox, DocumentMetadata, OcrResult, OcrStatus, OcrTextLine, ProcessingJobType
from app.services.document_storage import DocumentStorage
from app.services.document_parser import DeterministicInvoiceParser
from app.services import ocr as ocr_module
from app.services.ocr import MockOcrProvider, PaddleOcrProvider
from app.services.vector_indexing import VectorIndexingResult


@pytest.fixture(autouse=True)
def reset_selected_ocr_provider_cache() -> None:
    _reset_selected_ocr_provider_cache()
    yield
    _reset_selected_ocr_provider_cache()


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


def test_get_fields_returns_pending_before_parser_runs(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.txt", b"sample document", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.get(f"/documents/{document_id}/fields")

    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id
    assert body["status"] == "pending"
    assert body["parser_source"] == "deterministic_invoice"
    assert body["source_ocr_status"] == "pending"


def test_parse_document_fields_saves_parser_result_to_metadata(
    client: TestClient,
    tmp_path: Path,
) -> None:
    invoice_text = "\n".join(
        [
            "Fictitious Demo Invoice",
            "Invoice number: AUR-2026-051",
            "Vendor: Aurora Office Supplies Demo LLC",
            "Issue date: 2026-05-31",
            "Tax: USD 80.00",
            "Amount due: USD 1,248.50",
            "Line items:",
            "- 6 ergonomic chair kits at USD 149.00 each",
        ]
    )
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.txt", invoice_text.encode("utf-8"), "text/plain")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(f"/documents/{document_id}/parse")

    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == document_id
    assert body["status"] == "parsed"
    assert body["fields"]["invoice_number"]["value"] == "AUR-2026-051"
    assert body["fields"]["vendor_name"]["value"] == "Aurora Office Supplies Demo LLC"
    assert body["fields"]["issue_date"]["value"] == "2026-05-31"
    assert body["fields"]["total_amount"]["value"] == 1248.5
    assert body["fields"]["tax_amount"]["value"] == 80.0
    assert body["fields"]["currency"]["value"] == "USD"
    assert body["fields"]["invoice_number"]["parser_source"] == "deterministic_invoice"
    assert body["fields"]["invoice_number"]["source_text"] == "Invoice number: AUR-2026-051"
    assert body["fallback_reason"] is None

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata[0]["parser_result"]["status"] == "parsed"
    assert metadata[0]["parser_result"]["fields"]["invoice_number"]["value"] == "AUR-2026-051"
    assert metadata[0]["processing"]["parser"] == "completed"
    assert [job["job_type"] for job in metadata[0]["processing_jobs"]] == [
        "upload",
        "ocr_mock",
        "local_indexing",
        "parser",
    ]
    assert metadata[0]["latest_job"]["job_type"] == "parser"
    assert metadata[0]["latest_job"]["status"] == "completed"


def test_get_fields_returns_saved_parser_result_after_storage_reload(
    client: TestClient,
    tmp_path: Path,
) -> None:
    invoice_text = "\n".join(
        [
            "Invoice number: ORN-2026-118",
            "Vendor: Orion Analytics Demo Software",
            "Issue date: 2026-06-01",
            "Amount due: USD 3,888.00",
        ]
    )
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.txt", invoice_text.encode("utf-8"), "text/plain")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")
    client.post(f"/documents/{document_id}/parse")
    app.dependency_overrides[get_document_storage] = lambda: DocumentStorage(tmp_path / "data")

    response = client.get(f"/documents/{document_id}/fields")

    assert response.status_code == 200
    assert response.json()["status"] == "parsed"
    assert response.json()["fields"]["invoice_number"]["value"] == "ORN-2026-118"


def test_parse_document_fields_rejects_document_before_ocr(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.txt", b"sample document", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/parse")

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["document_id"] == document_id
    assert detail["status"] == "failed"
    assert detail["fallback_reason"] == "ocr_not_completed"
    assert detail["fields"]["invoice_number"]["value"] is None
    assert detail["fields"]["invoice_number"]["fallback_reason"] is None


def test_parse_document_fields_returns_404_for_unknown_document(client: TestClient) -> None:
    response = client.post("/documents/not-found/parse")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_get_fields_returns_404_for_unknown_document(client: TestClient) -> None:
    response = client.get("/documents/not-found/fields")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_parse_document_fields_keeps_missing_fields_as_metadata(client: TestClient) -> None:
    invoice_text = "\n".join(
        [
            "Invoice number: INV-2026-001",
            "Amount due: USD 10.00",
        ]
    )
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.txt", invoice_text.encode("utf-8"), "text/plain")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(f"/documents/{document_id}/parse")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "parsed"
    assert body["fallback_reason"] == "missing_fields"
    assert body["fields"]["invoice_number"]["value"] == "INV-2026-001"
    assert body["fields"]["vendor_name"]["value"] is None
    assert body["fields"]["vendor_name"]["fallback_reason"] == "field_not_found"
    assert "vendor_name" in body["trace_metadata"]["missing_fields"]


def test_parse_document_fields_uses_parser_dependency_override(client: TestClient) -> None:
    class StubParser(DeterministicInvoiceParser):
        def parse(self, document: DocumentMetadata, parsed_at: datetime | None = None):
            result = super().parse(document, parsed_at)
            result.trace_metadata["stub_parser"] = "true"
            return result

    app.dependency_overrides[get_document_parser] = StubParser
    invoice_text = "\n".join(
        [
            "Invoice number: INV-2026-002",
            "Vendor: Stub Demo Vendor",
            "Issue date: 2026-05-24",
            "Tax: USD 1.00",
            "Total: USD 11.00",
        ]
    )
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.txt", invoice_text.encode("utf-8"), "text/plain")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(f"/documents/{document_id}/parse")

    assert response.status_code == 200
    assert response.json()["trace_metadata"]["stub_parser"] == "true"


def test_vector_indexing_endpoint_returns_indexing_result(client: TestClient) -> None:
    class StubVectorIndexingService:
        def __init__(self) -> None:
            self.document: DocumentMetadata | None = None

        def index_document(self, document: DocumentMetadata) -> VectorIndexingResult:
            self.document = document
            return VectorIndexingResult(
                document_id=document.document_id,
                status="completed",
                indexed_chunk_count=1,
                point_ids=["point-001"],
                collection_name="docurag_chunks_v1",
                vector_size=1024,
                embedding_provider="ollama",
                embedding_model="qwen3-embedding:0.6b",
            )

    service = StubVectorIndexingService()
    app.dependency_overrides[get_vector_indexing_service] = lambda: service
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(f"/documents/{document_id}/index/vector")

    assert response.status_code == 200
    assert service.document is not None
    assert service.document.document_id == document_id
    assert service.document.chunks[0].chunk_id == f"{document_id}-chunk-001"
    assert response.json() == {
        "document_id": document_id,
        "status": "completed",
        "indexed_chunk_count": 1,
        "skipped_chunk_count": 0,
        "point_ids": ["point-001"],
        "collection_name": "docurag_chunks_v1",
        "vector_size": 1024,
        "embedding_provider": "ollama",
        "embedding_model": "qwen3-embedding:0.6b",
        "reason": None,
        "error": None,
    }


def test_vector_indexing_endpoint_returns_404_for_unknown_document(client: TestClient) -> None:
    response = client.post("/documents/not-found/index/vector")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_vector_indexing_endpoint_rejects_document_before_ocr(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.post(f"/documents/{document_id}/index/vector")

    assert response.status_code == 409
    assert response.json()["detail"] == {
        "document_id": document_id,
        "status": "failed",
        "error": "Document OCR must be completed before vector indexing.",
    }


def test_vector_indexing_endpoint_returns_skipped_for_empty_chunks(
    client: TestClient,
    tmp_path: Path,
) -> None:
    class StubVectorIndexingService:
        def index_document(self, document: DocumentMetadata) -> VectorIndexingResult:
            assert document.chunks == []
            return VectorIndexingResult(
                document_id=document.document_id,
                status="skipped",
                skipped_chunk_count=0,
                collection_name="docurag_chunks_v1",
                vector_size=1024,
                embedding_provider="ollama",
                embedding_model="qwen3-embedding:0.6b",
                reason="Document has no chunks to index.",
            )

    app.dependency_overrides[get_vector_indexing_service] = StubVectorIndexingService
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    metadata_path = tmp_path / "data" / "documents.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata[0]["chunks"] = []
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    response = client.post(f"/documents/{document_id}/index/vector")

    assert response.status_code == 200
    assert response.json()["status"] == "skipped"
    assert response.json()["reason"] == "Document has no chunks to index."


def test_vector_indexing_endpoint_returns_503_when_provider_disabled(client: TestClient) -> None:
    class DisabledVectorIndexingService:
        def index_document(self, document: DocumentMetadata) -> VectorIndexingResult:
            return VectorIndexingResult(
                document_id=document.document_id,
                status="failed",
                collection_name="docurag_chunks_v1",
                vector_size=1024,
                embedding_provider="disabled",
                error="Set DOCURAG_EMBEDDING_PROVIDER=ollama to enable local embeddings.",
            )

    app.dependency_overrides[get_vector_indexing_service] = DisabledVectorIndexingService
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(f"/documents/{document_id}/index/vector")

    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "failed"
    assert response.json()["detail"]["embedding_provider"] == "disabled"
    assert "DOCURAG_EMBEDDING_PROVIDER=ollama" in response.json()["detail"]["error"]


def test_vector_indexing_endpoint_returns_503_when_qdrant_fails(client: TestClient) -> None:
    class FailingVectorIndexingService:
        def index_document(self, document: DocumentMetadata) -> VectorIndexingResult:
            return VectorIndexingResult(
                document_id=document.document_id,
                status="failed",
                collection_name="docurag_chunks_v1",
                vector_size=1024,
                embedding_provider="ollama",
                embedding_model="qwen3-embedding:0.6b",
                error="Cannot connect to Qdrant",
            )

    app.dependency_overrides[get_vector_indexing_service] = FailingVectorIndexingService
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(f"/documents/{document_id}/index/vector")

    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "failed"
    assert response.json()["detail"]["error"] == "Cannot connect to Qdrant"


def test_selected_ocr_default_provider_is_paddleocr() -> None:
    get_settings.cache_clear()

    try:
        provider = get_selected_ocr_provider()
    finally:
        get_settings.cache_clear()

    assert isinstance(provider, PaddleOcrProvider)
    assert provider.language == "ch"
    assert provider.ocr_version == "PP-OCRv4"
    assert provider.det_model_name == "PP-OCRv4_mobile_det"
    assert provider.rec_model_name == "PP-OCRv4_mobile_rec"
    assert provider.cls_model_name == "ch_ppocr_mobile_v2.0_cls"
    assert provider.use_angle_cls is False
    assert provider.det_limit_side_len == 960
    assert provider.rec_batch_num == 6


def test_selected_ocr_provider_preload_reuses_process_engine(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class StubPaddleEngine:
        def __init__(self) -> None:
            self.ocr_calls = 0

        def ocr(self, file_path: str, cls: bool = True):
            assert file_path.endswith("real-provider.png")
            assert cls is False
            self.ocr_calls += 1
            return [
                (
                    [[10, 20], [180, 20], [180, 44], [10, 44]],
                    (f"Preloaded OCR call {self.ocr_calls}", 0.96),
                )
            ]

    engine = StubPaddleEngine()
    load_calls = 0

    def fake_load_engine(self: PaddleOcrProvider):
        nonlocal load_calls

        if self._engine is None:
            load_calls += 1
            self._engine = engine

        return self._engine

    monkeypatch.setattr(PaddleOcrProvider, "_load_engine", fake_load_engine)

    preload_selected_ocr_provider()
    provider = get_selected_ocr_provider()

    assert isinstance(provider, PaddleOcrProvider)
    assert load_calls == 1

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("real-provider.png", b"fake image", "image/png")},
    )
    document_id = upload_response.json()["document_id"]

    first_response = client.post(f"/documents/{document_id}/ocr")
    second_response = client.post(f"/documents/{document_id}/ocr")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["text"] == "Preloaded OCR call 1"
    assert second_response.json()["text"] == "Preloaded OCR call 2"
    assert load_calls == 1
    assert engine.ocr_calls == 2


def test_paddleocr_preload_failure_raises_without_mock_fallback(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fake_load_engine(self: PaddleOcrProvider):
        raise RuntimeError("preload failed")

    monkeypatch.setattr(PaddleOcrProvider, "_load_engine", fake_load_engine)

    with caplog.at_level("ERROR"), pytest.raises(RuntimeError, match="preload failed"):
        preload_selected_ocr_provider()

    provider = get_selected_ocr_provider()

    assert isinstance(provider, PaddleOcrProvider)
    assert "PaddleOCR provider preload failed during backend startup." in caplog.text


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
            assert cls is False
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
    assert result.extracted_fields["ocr_language"] == "ch"
    assert result.extracted_fields["ocr_version"] == "PP-OCRv4"
    assert result.extracted_fields["det_model"] == "PP-OCRv4_mobile_det"
    assert result.extracted_fields["rec_model"] == "PP-OCRv4_mobile_rec"
    assert result.extracted_fields["cls_model"] == "ch_ppocr_mobile_v2.0_cls"
    assert result.extracted_fields["use_angle_cls"] == "false"
    assert result.extracted_fields["det_limit_side_len"] == "960"
    assert result.extracted_fields["rec_batch_num"] == "6"
    assert result.extracted_fields["det_model_dir"].endswith("ch_PP-OCRv4_det_infer")
    assert result.extracted_fields["rec_model_dir"].endswith("ch_PP-OCRv4_rec_infer")
    assert result.extracted_fields["cls_model_dir"].endswith("ch_ppocr_mobile_v2.0_cls_infer")
    assert result.extracted_fields["engine_preloaded_before_request"] == "true"
    assert float(result.extracted_fields["timing_engine_load_ms"]) >= 0
    assert float(result.extracted_fields["timing_inference_ms"]) >= 0
    assert float(result.extracted_fields["timing_normalization_ms"]) >= 0
    assert float(result.extracted_fields["timing_total_ms"]) >= 0
    assert [line.page_number for line in result.lines] == [1, 1]
    assert result.lines[0].bbox == BoundingBox(x_min=10, y_min=20, x_max=180, y_max=44)
    assert result.lines[0].confidence == 0.96
    assert result.lines[0].metadata == {
        "ocr_provider": "paddleocr",
        "ocr_language": "ch",
        "ocr_version": "PP-OCRv4",
        "det_model": "PP-OCRv4_mobile_det",
        "rec_model": "PP-OCRv4_mobile_rec",
        "cls_model": "ch_ppocr_mobile_v2.0_cls",
        "use_angle_cls": "false",
        "line_index": "1",
    }


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


def test_paddleocr_provider_requires_cuda_paddle_build(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class SupportedVersionInfo:
        major = 3
        minor = 12
        micro = 10

    class PaddleDevice:
        @staticmethod
        def is_compiled_with_cuda() -> bool:
            return False

    class PaddleUtils:
        @staticmethod
        def run_check() -> None:
            return None

    monkeypatch.setattr(ocr_module.sys, "version_info", SupportedVersionInfo())
    monkeypatch.setitem(
        sys.modules,
        "paddle",
        SimpleNamespace(
            __version__="3.3.0",
            device=PaddleDevice,
            utils=PaddleUtils,
        ),
    )

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
    assert result.extracted_fields["error_code"] == "paddleocr_gpu_required"
    assert "CUDA-enabled PaddlePaddle runtime" in result.extracted_fields["error"]


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
