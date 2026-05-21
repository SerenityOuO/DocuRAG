import pytest
from pydantic import ValidationError

from app.schemas.documents import (
    DocumentChunk,
    DocumentMetadata,
    DocumentStatus,
    DocumentUploadResponse,
    OcrResult,
    OcrStatus,
    ProcessingStepStatus,
)
from app.schemas.rag import RagQueryRequest


def test_document_status_values() -> None:
    assert DocumentStatus.UPLOADED == "uploaded"
    assert DocumentStatus.PROCESSING == "processing"
    assert DocumentStatus.READY == "ready"
    assert DocumentStatus.FAILED == "failed"


def test_ocr_status_values() -> None:
    assert OcrStatus.PENDING == "pending"
    assert OcrStatus.RUNNING == "running"
    assert OcrStatus.COMPLETED == "completed"
    assert OcrStatus.FAILED == "failed"


def test_processing_step_status_values() -> None:
    assert ProcessingStepStatus.PENDING == "pending"
    assert ProcessingStepStatus.RUNNING == "running"
    assert ProcessingStepStatus.COMPLETED == "completed"
    assert ProcessingStepStatus.FAILED == "failed"


def test_document_processing_status_defaults() -> None:
    document = DocumentUploadResponse(
        document_id="doc_001",
        filename="invoice.pdf",
        stored_filename="doc_001-invoice.pdf",
        file_type="pdf",
        content_type="application/pdf",
        size=12,
        status=DocumentStatus.UPLOADED,
        created_at="2026-05-20T00:00:00Z",
    )

    assert document.processing.upload == ProcessingStepStatus.COMPLETED
    assert document.processing.ocr == ProcessingStepStatus.PENDING
    assert document.processing.indexing == ProcessingStepStatus.PENDING
    assert document.processing.ready is False
    assert document.processing.failed_reason is None


def test_legacy_ready_metadata_infers_processing_status() -> None:
    document = DocumentMetadata.model_validate(
        {
            "document_id": "doc_001",
            "filename": "invoice.pdf",
            "stored_filename": "doc_001-invoice.pdf",
            "file_type": "pdf",
            "content_type": "application/pdf",
            "size": 12,
            "status": "ready",
            "created_at": "2026-05-20T00:00:00Z",
            "ocr": {
                "status": "completed",
                "text": "Mock OCR result",
                "extracted_fields": {},
                "updated_at": "2026-05-20T00:01:00Z",
            },
            "chunks": [
                {
                    "chunk_id": "doc_001-chunk-001",
                    "document_id": "doc_001",
                    "text": "Mock OCR result",
                    "source": "ocr_mock",
                    "created_at": "2026-05-20T00:01:00Z",
                }
            ],
        }
    )

    assert document.processing.upload == ProcessingStepStatus.COMPLETED
    assert document.processing.ocr == ProcessingStepStatus.COMPLETED
    assert document.processing.indexing == ProcessingStepStatus.COMPLETED
    assert document.processing.ready is True


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
