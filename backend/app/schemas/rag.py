from pydantic import BaseModel, Field

from app.schemas.documents import DocumentChunk


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


class RagQueryResponse(BaseModel):
    answer: str
    citations: list[RagCitation]
    retrieved_chunks: list[RetrievedChunk]
