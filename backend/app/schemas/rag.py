from pydantic import BaseModel, Field

from app.schemas.documents import BoundingBox, DocumentChunk


class RagQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class RetrievedChunk(DocumentChunk):
    filename: str = Field(..., min_length=1)
    score: float = Field(..., ge=0)


class RagCitation(BaseModel):
    document_id: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    chunk_id: str = Field(..., min_length=1)
    page_number: int | None = Field(default=None, ge=1)
    bbox: BoundingBox | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_type: str | None = Field(default=None, min_length=1)
    trace_metadata: dict[str, str] = Field(default_factory=dict)


class RagQueryResponse(BaseModel):
    answer: str
    citations: list[RagCitation]
    retrieved_chunks: list[RetrievedChunk]
