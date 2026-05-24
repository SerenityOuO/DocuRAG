from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.rag import get_rag_provider
from app.core.config import get_settings
from app.schemas.agent import AgentRun, AgentRunRequest
from app.services.agent import AgentService
from app.services.agent_tools import AgentToolService
from app.services.document_storage import DocumentStorage
from app.services.rag import RagProvider


router = APIRouter(prefix="/agent", tags=["agent"])


def get_document_storage() -> DocumentStorage:
    settings = get_settings()
    return DocumentStorage(settings.data_dir)


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]
RagProviderDep = Annotated[RagProvider, Depends(get_rag_provider)]


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
    service: AgentServiceDep,
) -> AgentRun:
    return service.run(request)


@router.get("/runs/{run_id}", response_model=AgentRun)
async def get_agent_run(
    run_id: str,
    storage: DocumentStorageDep,
) -> AgentRun:
    agent_run = storage.get_agent_run(run_id)

    if agent_run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")

    return agent_run
