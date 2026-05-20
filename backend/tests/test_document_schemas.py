import pytest
from pydantic import ValidationError

from app.schemas.documents import DocumentStatus, DocumentUploadResponse


def test_document_status_values() -> None:
    assert DocumentStatus.UPLOADED == "uploaded"
    assert DocumentStatus.PROCESSING == "processing"
    assert DocumentStatus.READY == "ready"
    assert DocumentStatus.FAILED == "failed"


def test_document_response_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        DocumentUploadResponse(
            document_id="doc_001",
            filename="invoice.pdf",
            stored_filename="doc_001-invoice.pdf",
            file_type="pdf",
            content_type="application/pdf",
            size=12,
            status="ocr_processing",
            created_at="2026-05-20T00:00:00Z",
        )
