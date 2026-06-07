from typing import Annotated
from hashlib import sha256
import json

from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.auth import (
    RequestAuthContext,
    require_authenticated_user,
)
from app.core.config import get_settings
from app.repositories.document_metadata import create_document_storage
from app.schemas.rag import RagQueryRequest, RagQueryResponse
from app.schemas.documents import DocumentMetadata
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
from app.services.redis_runtime import create_redis_runtime
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
    settings = get_settings()
    project_ids = auth_user.project_ids if auth_user is not None else None
    documents = storage.list_documents_for_rag(project_ids)
    redis_runtime = create_redis_runtime(settings)
    rate_limit = redis_runtime.check_rate_limit(
        _rate_limit_key(auth_user),
        settings.redis_rate_limit_per_minute,
        settings.redis_rate_limit_window_seconds,
    )
    if not rate_limit.allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "status": "rate_limited",
                "error": "Too many RAG queries. Please retry after the current window.",
                "limit": rate_limit.limit,
                "retry_after_seconds": rate_limit.retry_after_seconds,
            },
        )

    cache_key = _rag_cache_key(settings, request, documents, auth_user)
    cached = redis_runtime.get_query_cache(cache_key)
    if cached.response is not None:
        return _annotate_redis_trace(cached.response, cached.status, rate_limit.status)

    response = provider.query(request.query, request.top_k, documents)
    stored = redis_runtime.set_query_cache(cache_key, response)
    cache_status = stored.status if cached.status == "miss" else cached.status
    return _annotate_redis_trace(response, cache_status, rate_limit.status)


def _rate_limit_key(auth_user: RequestAuthContext | None) -> str:
    if auth_user is None:
        return "rag-query:anonymous"

    organization = auth_user.organization_id or "no-org"
    project = auth_user.active_project_id or "no-project"
    return f"rag-query:{auth_user.auth_mode}:{organization}:{project}:{auth_user.username}:{auth_user.role}"


def _rag_cache_key(
    settings,
    request: RagQueryRequest,
    documents: list[DocumentMetadata],
    auth_user: RequestAuthContext | None,
) -> str:
    document_signature = []
    for document in sorted(documents, key=lambda item: item.document_id):
        chunk_signature = [
            f"{chunk.chunk_id}:{chunk.source}:{chunk.created_at.isoformat()}"
            for chunk in sorted(document.chunks, key=lambda item: item.chunk_id)
        ]
        document_signature.append(
            {
                "document_id": document.document_id,
                "project_id": document.project_id,
                "status": document.status,
                "chunks": chunk_signature,
            }
        )

    payload = {
        "query": request.query,
        "top_k": request.top_k,
        "auth_mode": auth_user.auth_mode if auth_user is not None else "disabled",
        "role": auth_user.role if auth_user is not None else "anonymous",
        "organization_id": auth_user.organization_id if auth_user is not None else None,
        "project_ids": sorted(auth_user.project_ids) if auth_user is not None and auth_user.project_ids is not None else None,
        "rag_provider": settings.rag_retrieval_provider,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model,
        "rerank_provider": settings.rerank_provider,
        "rerank_model": settings.rerank_model,
        "documents": document_signature,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return sha256(encoded).hexdigest()


def _annotate_redis_trace(
    response: RagQueryResponse,
    query_cache_status: str,
    rate_limit_status: str,
) -> RagQueryResponse:
    trace_metadata = {}
    if query_cache_status != "disabled":
        trace_metadata["query_cache_status"] = query_cache_status
    if rate_limit_status != "disabled":
        trace_metadata["rate_limit_status"] = rate_limit_status

    if not trace_metadata:
        return response

    return response.model_copy(
        update={
            "citations": [
                citation.model_copy(
                    update={
                        "trace_metadata": {
                            **citation.trace_metadata,
                            **trace_metadata,
                        }
                    }
                )
                for citation in response.citations
            ],
            "retrieved_chunks": [
                chunk.model_copy(
                    update={
                        "metadata": {
                            **chunk.metadata,
                            **trace_metadata,
                        }
                    }
                )
                for chunk in response.retrieved_chunks
            ],
        }
    )
