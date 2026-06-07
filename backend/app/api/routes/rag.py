from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.routes.auth import (
    RequestAuthContext,
    require_authenticated_user,
)
from app.core.config import get_settings
from app.repositories.document_metadata import create_document_storage
from app.schemas.rag import RagQueryRequest, RagQueryResponse
from app.services.document_storage import DocumentStorage
from app.services.embedding import create_embedding_provider
from app.services.llm import create_llm_provider
from app.services.rag import (
    HybridRagProvider,
    HybridRerankRagProvider,
    KeywordRagProvider,
    RagProvider,
    VectorRagProvider,
    VectorRerankRagProvider,
)
from app.services.rerank import create_rerank_service
from app.services.vector_store import create_qdrant_vector_store


router = APIRouter(prefix="/rag", tags=["rag"])


def get_document_storage() -> DocumentStorage:
    return create_document_storage(get_settings())


def get_rag_provider() -> RagProvider:
    settings = get_settings()
    llm_provider = create_llm_provider(settings) if settings.llm_provider else None
    keyword_provider = KeywordRagProvider(llm_provider=llm_provider)
    retrieval_provider = settings.rag_retrieval_provider.strip().lower()

    if retrieval_provider not in {"vector", "vector_rerank", "hybrid", "hybrid_rerank"}:
        return keyword_provider

    vector_provider = VectorRagProvider(
        keyword_provider=keyword_provider,
        embedding_provider=create_embedding_provider(settings),
        vector_store=create_qdrant_vector_store(settings),
    )

    if retrieval_provider == "vector":
        return vector_provider

    if retrieval_provider == "vector_rerank":
        return VectorRerankRagProvider(
            vector_provider=vector_provider,
            response_builder=keyword_provider,
            rerank_service=create_rerank_service(settings),
        )

    hybrid_provider = HybridRagProvider(
        keyword_provider=keyword_provider,
        vector_provider=vector_provider,
    )

    if retrieval_provider == "hybrid":
        return hybrid_provider

    return HybridRerankRagProvider(
        hybrid_provider=hybrid_provider,
        response_builder=keyword_provider,
        rerank_service=create_rerank_service(settings),
    )


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]
RagProviderDep = Annotated[RagProvider, Depends(get_rag_provider)]
AuthenticatedUserDep = Annotated[RequestAuthContext | None, Depends(require_authenticated_user)]


@router.post("/query", response_model=RagQueryResponse)
async def query_rag(
    request: RagQueryRequest,
    storage: DocumentStorageDep,
    provider: RagProviderDep,
    auth_user: AuthenticatedUserDep,
) -> RagQueryResponse:
    project_ids = auth_user.project_ids if auth_user is not None else None
    return provider.query(request.query, request.top_k, storage.list_documents_for_rag(project_ids))
