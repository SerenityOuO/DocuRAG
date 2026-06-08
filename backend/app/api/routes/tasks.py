from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.auth import RequestAuthContext, require_authenticated_user, require_project_access
from app.core.config import get_settings
from app.schemas.tasks import WorkerTaskListResponse, WorkerTaskRecord
from app.services.task_status import TaskStatusStore


router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_status_store() -> TaskStatusStore:
    settings = get_settings()
    return TaskStatusStore(settings.data_dir, settings=settings)


TaskStatusStoreDep = Annotated[TaskStatusStore, Depends(get_task_status_store)]
AuthenticatedUserDep = Annotated[RequestAuthContext | None, Depends(require_authenticated_user)]


@router.get("", response_model=WorkerTaskListResponse)
async def list_worker_tasks(
    task_store: TaskStatusStoreDep,
    auth_user: AuthenticatedUserDep,
) -> WorkerTaskListResponse:
    project_ids = auth_user.project_ids if auth_user is not None else None
    return WorkerTaskListResponse(tasks=task_store.list_tasks(project_ids))


@router.get("/{task_id}", response_model=WorkerTaskRecord)
async def get_worker_task(
    task_id: str,
    task_store: TaskStatusStoreDep,
    auth_user: AuthenticatedUserDep,
) -> WorkerTaskRecord:
    task = task_store.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    require_project_access(auth_user, task.project_id)
    return task
