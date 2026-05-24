from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.rag import RagCitation, RetrievedChunk


class AgentToolStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


AgentToolName = Literal[
    "get_document_fields",
    "search_documents",
    "summarize_invoice_fields",
]


class AgentToolObservation(BaseModel):
    status: AgentToolStatus
    message: str = Field(..., min_length=1)
    missing_fields: list[str] = Field(default_factory=list)
    fallback_reason: str | None = None


class AgentToolCall(BaseModel):
    tool_name: AgentToolName
    status: AgentToolStatus
    input_summary: str = Field(..., min_length=1)
    output_summary: str | None = None
    observation: AgentToolObservation
    output: dict[str, Any] = Field(default_factory=dict)
    citations: list[RagCitation] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    trace_metadata: dict[str, str] = Field(default_factory=dict)
    error_message: str | None = None


class AgentRunRequest(BaseModel):
    task: str = Field(..., min_length=1)
    document_id: str | None = Field(default=None, min_length=1)
    query: str | None = Field(default=None, min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class AgentStep(BaseModel):
    step_id: str = Field(..., min_length=1)
    order: int = Field(..., ge=1)
    title: str = Field(..., min_length=1)
    tool_name: AgentToolName | None = None
    status: AgentRunStatus
    input_summary: str | None = None
    observation_summary: str | None = None
    fallback_reason: str | None = None


class AgentFinalAnswer(BaseModel):
    text: str = ""
    status: AgentRunStatus
    fallback_reason: str | None = None


class AgentRun(BaseModel):
    run_id: str = Field(..., min_length=1)
    status: AgentRunStatus
    task: str = Field(..., min_length=1)
    document_id: str | None = None
    query: str | None = None
    plan_steps: list[AgentStep] = Field(default_factory=list)
    tool_calls: list[AgentToolCall] = Field(default_factory=list)
    final_answer: AgentFinalAnswer
    citations: list[RagCitation] = Field(default_factory=list)
    trace: dict[str, str] = Field(default_factory=dict)
    created_at: str
    updated_at: str
