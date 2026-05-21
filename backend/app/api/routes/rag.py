from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.schemas.rag import RagCitation, RagQueryRequest, RagQueryResponse
from app.services.document_storage import DocumentStorage


router = APIRouter(prefix="/rag", tags=["rag"])


def get_document_storage() -> DocumentStorage:
    settings = get_settings()
    return DocumentStorage(settings.data_dir)


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]


@router.post("/query", response_model=RagQueryResponse)
async def query_rag(
    request: RagQueryRequest,
    storage: DocumentStorageDep,
) -> RagQueryResponse:
    retrieved_chunks = storage.search_chunks(request.query, request.top_k)
    citations = [
        RagCitation(
            document_id=chunk.document_id,
            filename=chunk.filename,
            chunk_id=chunk.chunk_id,
        )
        for chunk in retrieved_chunks
    ]

    if not retrieved_chunks:
        answer = (
            f"No OCR mock chunks matched query: {request.query}. "
            "Upload a document, run Mock OCR, then query again."
        )
    else:
        evidence_lines = [
            f"{index}. [{chunk.filename} / {chunk.chunk_id}] {chunk.text}"
            for index, chunk in enumerate(retrieved_chunks, start=1)
        ]
        answer = "Local OCR mock chunks matched the query:\n" + "\n".join(evidence_lines)

    return RagQueryResponse(
        answer=answer,
        citations=citations,
        retrieved_chunks=retrieved_chunks,
    )
