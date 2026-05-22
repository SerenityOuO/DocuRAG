from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.schemas.rag import RagQueryRequest, RagQueryResponse
from app.services.document_storage import DocumentStorage
from app.services.llm import create_llm_provider
from app.services.rag import KeywordRagProvider


router = APIRouter(prefix="/rag", tags=["rag"])


def get_document_storage() -> DocumentStorage:
    settings = get_settings()
    return DocumentStorage(settings.data_dir)


def get_rag_provider() -> KeywordRagProvider:
    settings = get_settings()
    llm_provider = create_llm_provider(settings) if settings.llm_provider else None
    return KeywordRagProvider(llm_provider=llm_provider)


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]
RagProviderDep = Annotated[KeywordRagProvider, Depends(get_rag_provider)]


@router.post("/query", response_model=RagQueryResponse)
async def query_rag(
    request: RagQueryRequest,
    storage: DocumentStorageDep,
    provider: RagProviderDep,
) -> RagQueryResponse:
    return provider.query(request.query, request.top_k, storage.list_documents_for_rag())
