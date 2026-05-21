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


class ProcessingJobType(StrEnum):
    UPLOAD = "upload"
    OCR_MOCK = "ocr_mock"
    OCR_REAL = "ocr_real"
    LOCAL_INDEXING = "local_indexing"


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


class ProcessingJob(BaseModel):
    job_id: str = Field(..., min_length=1)
    document_id: str = Field(..., min_length=1)
    job_type: ProcessingJobType
    status: ProcessingStepStatus
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None

    @model_validator(mode="after")
    def validate_updated_at(self):
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must be greater than or equal to created_at")
        return self


class OcrResult(BaseModel):
    status: OcrStatus = OcrStatus.PENDING
    text: str = ""
    extracted_fields: dict[str, str] = Field(default_factory=dict)
    updated_at: datetime | None = None


class BoundingBox(BaseModel):
    x_min: float = Field(..., ge=0)
    y_min: float = Field(..., ge=0)
    x_max: float = Field(..., ge=0)
    y_max: float = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_edges(self):
        if self.x_max < self.x_min:
            raise ValueError("x_max must be greater than or equal to x_min")
        if self.y_max < self.y_min:
            raise ValueError("y_max must be greater than or equal to y_min")
        return self


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., min_length=1)
    document_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    created_at: datetime
    page_number: int | None = Field(default=None, ge=1)
    bbox: BoundingBox | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_type: str = Field(default="ocr_mock", min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)


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
    processing_jobs: list[ProcessingJob] = Field(default_factory=list)
    latest_job: ProcessingJob | None = None

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
