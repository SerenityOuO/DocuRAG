from datetime import datetime
from enum import StrEnum
from typing import Literal

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
    PARSER = "parser"


class OcrStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ParserStatus(StrEnum):
    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


ParserSource = Literal["deterministic_invoice", "llm_invoice", "vlm_invoice"]
FieldValue = str | int | float | bool


class ProcessingStatus(BaseModel):
    upload: ProcessingStepStatus = ProcessingStepStatus.COMPLETED
    ocr: ProcessingStepStatus = ProcessingStepStatus.PENDING
    indexing: ProcessingStepStatus = ProcessingStepStatus.PENDING
    parser: ProcessingStepStatus = ProcessingStepStatus.PENDING
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


class OcrTextLine(BaseModel):
    text: str = Field(..., min_length=1)
    page_number: int | None = Field(default=None, ge=1)
    bbox: BoundingBox | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    metadata: dict[str, str] = Field(default_factory=dict)


class OcrResult(BaseModel):
    status: OcrStatus = OcrStatus.PENDING
    text: str = ""
    extracted_fields: dict[str, str] = Field(default_factory=dict)
    lines: list[OcrTextLine] = Field(default_factory=list)
    updated_at: datetime | None = None


class ExtractedField(BaseModel):
    value: FieldValue | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_text: str | None = None
    source_page: int | None = Field(default=None, ge=1)
    source_bbox: BoundingBox | None = None
    parser_source: ParserSource = "deterministic_invoice"
    fallback_reason: str | None = None


class InvoiceLineItem(BaseModel):
    description: ExtractedField = Field(default_factory=ExtractedField)
    quantity: ExtractedField = Field(default_factory=ExtractedField)
    unit_price: ExtractedField = Field(default_factory=ExtractedField)
    amount: ExtractedField = Field(default_factory=ExtractedField)


class DocumentFields(BaseModel):
    document_type: ExtractedField = Field(default_factory=ExtractedField)
    vendor_name: ExtractedField = Field(default_factory=ExtractedField)
    invoice_number: ExtractedField = Field(default_factory=ExtractedField)
    issue_date: ExtractedField = Field(default_factory=ExtractedField)
    total_amount: ExtractedField = Field(default_factory=ExtractedField)
    tax_amount: ExtractedField = Field(default_factory=ExtractedField)
    currency: ExtractedField = Field(default_factory=ExtractedField)
    line_items: list[InvoiceLineItem] = Field(default_factory=list)


class ParserResult(BaseModel):
    document_id: str = Field(..., min_length=1)
    status: ParserStatus = ParserStatus.PENDING
    parser_source: ParserSource = "deterministic_invoice"
    schema_version: str = "invoice_fields_v1"
    fields: DocumentFields = Field(default_factory=DocumentFields)
    fallback_reason: str | None = None
    error_message: str | None = None
    source_ocr_status: OcrStatus | None = None
    source_ocr_updated_at: datetime | None = None
    updated_at: datetime | None = None
    trace_metadata: dict[str, str] = Field(default_factory=dict)


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
    parser_result: ParserResult | None = None
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


class VectorIndexingResponse(BaseModel):
    document_id: str = Field(..., min_length=1)
    status: Literal["completed", "skipped", "failed"]
    indexed_chunk_count: int = Field(default=0, ge=0)
    skipped_chunk_count: int = Field(default=0, ge=0)
    point_ids: list[str] = Field(default_factory=list)
    collection_name: str | None = None
    vector_size: int | None = Field(default=None, ge=1)
    embedding_provider: str | None = None
    embedding_model: str | None = None
    reason: str | None = None
    error: str | None = None
