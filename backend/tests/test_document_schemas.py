import pytest
from pydantic import ValidationError

from app.schemas.documents import (
    DocumentChunk,
    DocumentStatus,
    DocumentUploadResponse,
    OcrResult,
    OcrStatus,
)
from app.schemas.rag import RagQueryRequest


def test_document_status_values() -> None:
    assert DocumentStatus.UPLOADED == "uploaded"
    assert DocumentStatus.PROCESSING == "processing"
    assert DocumentStatus.READY == "ready"
    assert DocumentStatus.FAILED == "failed"


def test_ocr_status_values() -> None:
    assert OcrStatus.PENDING == "pending"
    assert OcrStatus.COMPLETED == "completed"
    assert OcrStatus.FAILED == "failed"


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


def test_ocr_result_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        OcrResult(status="ocr_processing")


def test_document_chunk_rejects_empty_text() -> None:
    with pytest.raises(ValidationError):
        DocumentChunk(
            chunk_id="chunk-001",
            document_id="doc-001",
            text="",
            source="ocr_mock",
            created_at="2026-05-20T00:00:00Z",
        )


def test_rag_query_rejects_invalid_top_k() -> None:
    with pytest.raises(ValidationError):
        RagQueryRequest(query="invoice", top_k=0)
