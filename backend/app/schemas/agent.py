from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.rag import RagCitation, RetrievedChunk


class AgentToolStatus(StrEnum):
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
