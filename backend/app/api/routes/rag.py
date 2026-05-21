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
            f"找不到與「{request.query}」相關的 OCR mock chunk。"
            "請先上傳文件、執行 Mock OCR，再重新查詢。"
        )
    else:
        evidence_lines = [
            f"{index}. [{chunk.filename} / {chunk.chunk_id}] {chunk.text}"
            for index, chunk in enumerate(retrieved_chunks, start=1)
        ]
        answer = "根據本機 OCR mock chunks，找到以下相關內容：\n" + "\n".join(evidence_lines)

    return RagQueryResponse(
        answer=answer,
        citations=citations,
        retrieved_chunks=retrieved_chunks,
    )
