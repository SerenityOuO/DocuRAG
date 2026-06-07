import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.routes.tasks import get_task_status_store
from app.core.config import Settings, get_settings
from app.main import app
from app.schemas.tasks import WorkerTaskRecord, WorkerTaskStatus, WorkerTaskType
from app.services.nats_runtime import create_nats_runtime
from app.services.task_status import TaskStatusStore
from workers.skeleton import WorkerSkeleton, run_smoke


def test_worker_task_record_validates_lifecycle_status() -> None:
    task = WorkerTaskRecord(
        task_id="task-001",
        task_type=WorkerTaskType.OCR,
        topic="document.ocr.requested",
        status=WorkerTaskStatus.QUEUED,
        document_id="doc-001",
        idempotency_key="document.ocr.requested:no-project:doc-001",
        created_at="2026-06-01T00:00:00Z",
        updated_at="2026-06-01T00:00:00Z",
    )

    assert task.status == WorkerTaskStatus.QUEUED
    assert task.task_type == WorkerTaskType.OCR

    with pytest.raises(ValidationError):
        WorkerTaskRecord(
            task_id="task-001",
            task_type=WorkerTaskType.OCR,
            topic="document.ocr.requested",
            status="completed",
            idempotency_key="document.ocr.requested:no-project:doc-001",
            created_at="2026-06-01T00:00:01Z",
            updated_at="2026-06-01T00:00:00Z",
        )


def test_task_status_store_creates_and_updates_worker_tasks(tmp_path: Path) -> None:
    store = TaskStatusStore(tmp_path)
    task = store.create_task(
        "document.index.requested",
        {
            "document_id": "doc-001",
            "project_id": "project-001",
        },
    )

    assert task.status == WorkerTaskStatus.QUEUED
    assert task.task_type == WorkerTaskType.INDEXING
    assert task.idempotency_key == "document.index.requested:project-001:doc-001"

    running = store.update_task(task.task_id, WorkerTaskStatus.RUNNING)
    succeeded = store.update_task(
        task.task_id,
        WorkerTaskStatus.SUCCEEDED,
        trace_metadata={"handler": "placeholder"},
    )

    assert running is not None
    assert running.status == WorkerTaskStatus.RUNNING
    assert running.attempt == 1
    assert succeeded is not None
    assert succeeded.status == WorkerTaskStatus.SUCCEEDED
    assert succeeded.finished_at is not None
    assert succeeded.trace_metadata["handler"] == "placeholder"


def test_in_memory_nats_publish_consume_updates_task_status(tmp_path: Path) -> None:
    async def run() -> None:
        settings = Settings(data_dir=tmp_path, nats_url="memory://")
        runtime = await create_nats_runtime(settings)
        store = TaskStatusStore(tmp_path)
        worker = WorkerSkeleton(store)
        subscribe_results = await worker.subscribe(runtime)
        task, publish_result = await worker.enqueue_task(
            runtime,
            "document.ocr.requested",
            {
                "document_id": "doc-001",
                "project_id": "project-001",
            },
        )
        final_task = store.get_task(task.task_id)

        assert [result.status for result in subscribe_results] == ["subscribed"] * 4
        assert publish_result.status == "published"
        assert final_task is not None
        assert final_task.status == WorkerTaskStatus.SUCCEEDED
        assert final_task.started_at is not None
        assert final_task.finished_at is not None
        assert final_task.trace_metadata["placeholder_result"] == "acknowledged"
        await runtime.close()

    asyncio.run(run())


def test_nats_unavailable_fallback_marks_task_failed(tmp_path: Path) -> None:
    async def run() -> None:
        settings = Settings(data_dir=tmp_path, nats_url=None)
        runtime = await create_nats_runtime(settings)
        store = TaskStatusStore(tmp_path)
        worker = WorkerSkeleton(store)
        task, publish_result = await worker.enqueue_task(
            runtime,
            "document.parse.requested",
            {"document_id": "doc-001"},
        )
        final_task = store.get_task(task.task_id)

        assert publish_result.status == "disabled"
        assert final_task is not None
        assert final_task.status == WorkerTaskStatus.FAILED
        assert final_task.error_code == "nats_unavailable"

    asyncio.run(run())


def test_worker_smoke_uses_memory_runtime(tmp_path: Path) -> None:
    task = asyncio.run(run_smoke(tmp_path / "smoke"))

    assert task.status == WorkerTaskStatus.SUCCEEDED
    assert task.topic == "document.ocr.requested"


def test_task_status_api_lists_and_filters_tasks(tmp_path: Path) -> None:
    store = TaskStatusStore(tmp_path)
    visible = store.create_task(
        "document.ocr.requested",
        {"document_id": "visible-doc", "project_id": "project-visible"},
    )
    store.create_task(
        "document.ocr.requested",
        {"document_id": "hidden-doc", "project_id": "project-hidden"},
    )
    app.dependency_overrides[get_task_status_store] = lambda: store
    client = TestClient(app)

    response = client.get("/tasks")
    detail_response = client.get(f"/tasks/{visible.task_id}")

    assert response.status_code == 200
    assert {task["task_id"] for task in response.json()["tasks"]} == {
        task.task_id for task in store.list_tasks()
    }
    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == "queued"

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()
