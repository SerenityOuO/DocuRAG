from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.auth import (
    RequestAuthContext,
    accessible_project_ids,
    require_authenticated_user,
    require_ingestion_user,
    require_project_access,
)
from app.api.routes.rag import get_rag_provider
from app.core.config import get_settings
from app.repositories.document_metadata import create_document_storage
from app.schemas.agent import AgentRun, AgentRunRequest
from app.services.agent import AgentService
from app.services.agent_tools import AgentToolService
from app.services.document_storage import DocumentStorage
from app.services.rag import RagProvider


router = APIRouter(prefix="/agent", tags=["agent"])


def get_document_storage() -> DocumentStorage:
    return create_document_storage(get_settings())


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]
RagProviderDep = Annotated[RagProvider, Depends(get_rag_provider)]
AuthenticatedUserDep = Annotated[RequestAuthContext | None, Depends(require_authenticated_user)]
IngestionUserDep = Annotated[RequestAuthContext | None, Depends(require_ingestion_user)]


def get_agent_service(
    storage: DocumentStorageDep,
    rag_provider: RagProviderDep,
) -> AgentService:
    tool_service = AgentToolService(storage, rag_provider=rag_provider)
    return AgentService(storage, tool_service)


AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]


@router.post("/run", response_model=AgentRun)
async def run_agent(
    request: AgentRunRequest,
    storage: DocumentStorageDep,
    rag_provider: RagProviderDep,
    auth_user: IngestionUserDep,
) -> AgentRun:
    if request.document_id and auth_user is not None and auth_user.project_ids is not None:
        document = storage.get_document(request.document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")
        require_project_access(auth_user, document.project_id)

    tool_service = AgentToolService(
        storage,
        rag_provider=rag_provider,
        project_ids=accessible_project_ids(auth_user),
    )
    service = AgentService(storage, tool_service)
    project_id = auth_user.active_project_id if auth_user is not None and auth_user.auth_mode == "formal" else None
    return service.run(request, project_id=project_id)


@router.get("/runs/{run_id}", response_model=AgentRun)
async def get_agent_run(
    run_id: str,
    storage: DocumentStorageDep,
    auth_user: AuthenticatedUserDep,
) -> AgentRun:
    agent_run = storage.get_agent_run(run_id)

    if agent_run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")

    project_id = agent_run.trace.get("project_id")
    if not project_id and agent_run.document_id:
        document = storage.get_document(agent_run.document_id)
        project_id = document.project_id if document is not None else None
    require_project_access(auth_user, project_id)

    return agent_run
