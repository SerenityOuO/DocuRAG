from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., min_length=1)
    project_id: str | None = None
    filename: str = Field(..., min_length=1)
    file_type: str = Field(..., min_length=1)
    content_type: str = Field(..., min_length=1)
    size: int = Field(..., ge=0)
    status: DocumentStatus
    created_at: datetime
