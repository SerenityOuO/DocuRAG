from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class WorkerTaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class WorkerTaskType(StrEnum):
    OCR = "ocr"
    PARSER = "parser"
    INDEXING = "indexing"
    EVAL = "eval"


class WorkerTaskRecord(BaseModel):
    task_id: str = Field(..., min_length=1)
    task_type: WorkerTaskType
    topic: str = Field(..., min_length=1)
    status: WorkerTaskStatus
    organization_id: str | None = None
    project_id: str | None = None
    document_id: str | None = None
    eval_run_id: str | None = None
    idempotency_key: str = Field(..., min_length=1)
    attempt: int = Field(default=0, ge=0)
    max_attempts: int = Field(default=3, ge=1)
    created_at: datetime
    started_at: datetime | None = None
    updated_at: datetime
    finished_at: datetime | None = None
    failure_reason: str | None = None
    error_code: str | None = None
    trace_metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_timestamps(self):
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must be greater than or equal to created_at")
        if self.started_at is not None and self.started_at < self.created_at:
            raise ValueError("started_at must be greater than or equal to created_at")
        if self.finished_at is not None and self.finished_at < self.created_at:
            raise ValueError("finished_at must be greater than or equal to created_at")
        return self


class WorkerTaskListResponse(BaseModel):
    tasks: list[WorkerTaskRecord]
