import pytest
from pydantic import ValidationError

from app.schemas.documents import (
    BoundingBox,
    DocumentChunk,
    DocumentMetadata,
    DocumentStatus,
    DocumentUploadResponse,
    OcrResult,
    OcrStatus,
    OcrTextLine,
    ProcessingJob,
    ProcessingJobType,
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


def test_processing_job_type_values() -> None:
    assert ProcessingJobType.UPLOAD == "upload"
    assert ProcessingJobType.OCR_MOCK == "ocr_mock"
    assert ProcessingJobType.OCR_REAL == "ocr_real"
    assert ProcessingJobType.LOCAL_INDEXING == "local_indexing"
    assert ProcessingJobType.PARSER == "parser"


def test_processing_job_validates_required_fields() -> None:
    job = ProcessingJob(
        job_id="job-001",
        document_id="doc-001",
        job_type=ProcessingJobType.OCR_MOCK,
        status=ProcessingStepStatus.COMPLETED,
        created_at="2026-05-20T00:00:00Z",
        updated_at="2026-05-20T00:00:01Z",
    )

    assert job.job_id == "job-001"
    assert job.job_type == ProcessingJobType.OCR_MOCK
    assert job.status == ProcessingStepStatus.COMPLETED


def test_processing_job_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        ProcessingJob(
            job_id="job-001",
            document_id="doc-001",
            job_type=ProcessingJobType.OCR_MOCK,
            status="queued",
            created_at="2026-05-20T00:00:00Z",
            updated_at="2026-05-20T00:00:01Z",
        )

    with pytest.raises(ValidationError):
        ProcessingJob(
            job_id="job-001",
            document_id="doc-001",
            job_type=ProcessingJobType.OCR_MOCK,
            status=ProcessingStepStatus.COMPLETED,
            created_at="2026-05-20T00:00:01Z",
            updated_at="2026-05-20T00:00:00Z",
        )


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
    assert document.processing.parser == ProcessingStepStatus.PENDING
    assert document.processing.ready is False
    assert document.processing.failed_reason is None
    assert document.processing_jobs == []
    assert document.latest_job is None


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
    assert document.chunks[0].page_number is None
    assert document.chunks[0].bbox is None
    assert document.chunks[0].confidence is None
    assert document.chunks[0].source_type == "ocr_mock"
    assert document.chunks[0].metadata == {}
    assert document.processing_jobs == []
    assert document.latest_job is None


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


def test_ocr_result_accepts_line_trace_metadata() -> None:
    result = OcrResult(
        status=OcrStatus.COMPLETED,
        text="Invoice number AUR-2026-051",
        lines=[
            OcrTextLine(
                text="Invoice number AUR-2026-051",
                page_number=1,
                bbox=BoundingBox(x_min=10, y_min=20, x_max=180, y_max=44),
                confidence=0.96,
                metadata={"ocr_provider": "paddleocr", "line_index": "1"},
            )
        ],
    )

    assert result.lines[0].page_number == 1
    assert result.lines[0].bbox is not None
    assert result.lines[0].confidence == 0.96
    assert result.lines[0].metadata == {"ocr_provider": "paddleocr", "line_index": "1"}


def test_ocr_text_line_rejects_invalid_trace_metadata() -> None:
    with pytest.raises(ValidationError):
        OcrTextLine(
            text="Invoice number AUR-2026-051",
            page_number=0,
            confidence=1.5,
        )


def test_document_chunk_rejects_empty_text() -> None:
    with pytest.raises(ValidationError):
        DocumentChunk(
            chunk_id="chunk-001",
            document_id="doc-001",
            text="",
            source="ocr_mock",
            created_at="2026-05-20T00:00:00Z",
        )


def test_document_chunk_accepts_optional_trace_metadata() -> None:
    chunk = DocumentChunk(
        chunk_id="chunk-001",
        document_id="doc-001",
        text="Mock OCR result",
        source="ocr_mock",
        created_at="2026-05-20T00:00:00Z",
        page_number=1,
        bbox=BoundingBox(x_min=0, y_min=0, x_max=100, y_max=40),
        confidence=0.98,
        source_type="ocr_mock",
        metadata={"provider": "ocr_mock"},
    )

    assert chunk.page_number == 1
    assert chunk.bbox is not None
    assert chunk.confidence == 0.98
    assert chunk.source_type == "ocr_mock"
    assert chunk.metadata == {"provider": "ocr_mock"}


def test_document_chunk_rejects_invalid_trace_metadata() -> None:
    with pytest.raises(ValidationError):
        DocumentChunk(
            chunk_id="chunk-001",
            document_id="doc-001",
            text="Mock OCR result",
            source="ocr_mock",
            created_at="2026-05-20T00:00:00Z",
            page_number=0,
            confidence=1.5,
        )

    with pytest.raises(ValidationError):
        BoundingBox(x_min=100, y_min=0, x_max=10, y_max=40)


def test_rag_query_rejects_invalid_top_k() -> None:
    with pytest.raises(ValidationError):
        RagQueryRequest(query="invoice", top_k=0)
