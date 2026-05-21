from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class ProcessingStepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class OcrStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStatus(BaseModel):
    upload: ProcessingStepStatus = ProcessingStepStatus.COMPLETED
    ocr: ProcessingStepStatus = ProcessingStepStatus.PENDING
    indexing: ProcessingStepStatus = ProcessingStepStatus.PENDING
    ready: bool = False
    failed_reason: str | None = None
    updated_at: datetime | None = None


class OcrResult(BaseModel):
    status: OcrStatus = OcrStatus.PENDING
    text: str = ""
    extracted_fields: dict[str, str] = Field(default_factory=dict)
    updated_at: datetime | None = None


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., min_length=1)
    document_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    created_at: datetime


class DocumentMetadata(BaseModel):
    document_id: str = Field(..., min_length=1)
    project_id: str | None = None
    filename: str = Field(..., min_length=1)
    stored_filename: str = Field(..., min_length=1)
    file_type: str = Field(..., min_length=1)
    content_type: str = Field(..., min_length=1)
    size: int = Field(..., ge=0)
    status: DocumentStatus
    created_at: datetime
    processing: ProcessingStatus = Field(default_factory=ProcessingStatus)
    ocr: OcrResult = Field(default_factory=OcrResult)
    chunks: list[DocumentChunk] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def infer_processing_for_legacy_metadata(cls, data: object) -> object:
        if not isinstance(data, dict) or "processing" in data:
            return data

        ocr = data.get("ocr") if isinstance(data.get("ocr"), dict) else {}
        chunks = data.get("chunks") if isinstance(data.get("chunks"), list) else []
        status = data.get("status")
        ocr_status = ocr.get("status", ProcessingStepStatus.PENDING)

        if status == DocumentStatus.FAILED or ocr_status == OcrStatus.FAILED:
            processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.FAILED,
                indexing=ProcessingStepStatus.PENDING,
                ready=False,
                failed_reason=ocr.get("extracted_fields", {}).get("error"),
                updated_at=ocr.get("updated_at"),
            )
        elif status == DocumentStatus.READY or (ocr_status == OcrStatus.COMPLETED and chunks):
            processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.COMPLETED,
                indexing=ProcessingStepStatus.COMPLETED,
                ready=True,
                updated_at=ocr.get("updated_at"),
            )
        elif status == DocumentStatus.PROCESSING or ocr_status == OcrStatus.RUNNING:
            processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.RUNNING,
                indexing=ProcessingStepStatus.PENDING,
                ready=False,
                updated_at=ocr.get("updated_at"),
            )
        else:
            processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.PENDING,
                indexing=ProcessingStepStatus.PENDING,
                ready=False,
                updated_at=ocr.get("updated_at"),
            )

        return {**data, "processing": processing}


class DocumentUploadResponse(DocumentMetadata):
    pass


class DocumentListResponse(BaseModel):
    documents: list[DocumentMetadata]


class DocumentDetailResponse(DocumentMetadata):
    pass


class OcrResultResponse(OcrResult):
    document_id: str = Field(..., min_length=1)
