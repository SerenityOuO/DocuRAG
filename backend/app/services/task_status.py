from datetime import UTC, datetime
import json
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.schemas.tasks import WorkerTaskRecord, WorkerTaskStatus, WorkerTaskType
from app.services.observability import emit_observability_event


TOPIC_TASK_TYPES = {
    "document.ocr.requested": WorkerTaskType.OCR,
    "document.parse.requested": WorkerTaskType.PARSER,
    "document.index.requested": WorkerTaskType.INDEXING,
    "rag.eval.requested": WorkerTaskType.EVAL,
}


class TaskStatusStore:
    def __init__(self, data_dir: Path, settings: Settings | None = None) -> None:
        self.data_dir = data_dir
        self.task_path = data_dir / "worker_tasks.json"
        self.settings = settings

    def list_tasks(self, project_ids: frozenset[str] | None = None) -> list[WorkerTaskRecord]:
        tasks = sorted(self._read_tasks(), key=lambda task: task.created_at, reverse=True)
        if project_ids is None:
            return tasks

        return [
            task
            for task in tasks
            if task.project_id is not None and task.project_id in project_ids
        ]

    def get_task(self, task_id: str) -> WorkerTaskRecord | None:
        for task in self._read_tasks():
            if task.task_id == task_id:
                return task

        return None

    def create_task(
        self,
        topic: str,
        payload: dict[str, object],
        max_attempts: int = 3,
    ) -> WorkerTaskRecord:
        task_type = task_type_for_topic(topic)
        now = datetime.now(UTC)
        task = WorkerTaskRecord(
            task_id=str(uuid4()),
            task_type=task_type,
            topic=topic,
            status=WorkerTaskStatus.QUEUED,
            organization_id=_optional_string(payload.get("organization_id")),
            project_id=_optional_string(payload.get("project_id")),
            document_id=_optional_string(payload.get("document_id")),
            eval_run_id=_optional_string(payload.get("eval_run_id")),
            idempotency_key=idempotency_key_for_task(topic, payload),
            max_attempts=max_attempts,
            created_at=now,
            updated_at=now,
            trace_metadata={
                "source": "nats_worker_skeleton",
                "topic": topic,
            },
        )
        tasks = self._read_tasks()
        tasks.append(task)
        self._write_tasks(tasks)
        self._emit_worker_event(task)
        return task

    def update_task(
        self,
        task_id: str,
        status: WorkerTaskStatus,
        *,
        failure_reason: str | None = None,
        error_code: str | None = None,
        trace_metadata: dict[str, str] | None = None,
    ) -> WorkerTaskRecord | None:
        tasks = self._read_tasks()
        now = datetime.now(UTC)

        for index, task in enumerate(tasks):
            if task.task_id != task_id:
                continue

            update = {
                "status": status,
                "updated_at": now,
                "failure_reason": failure_reason,
                "error_code": error_code,
                "trace_metadata": {
                    **task.trace_metadata,
                    **(trace_metadata or {}),
                },
            }
            if status == WorkerTaskStatus.RUNNING and task.started_at is None:
                update["started_at"] = now
                update["attempt"] = task.attempt + 1
            if status in {
                WorkerTaskStatus.SUCCEEDED,
                WorkerTaskStatus.FAILED,
                WorkerTaskStatus.CANCELLED,
            }:
                update["finished_at"] = now

            updated_task = task.model_copy(update=update)
            tasks[index] = updated_task
            self._write_tasks(tasks)
            self._emit_worker_event(updated_task)
            return updated_task

        return None

    def _emit_worker_event(self, task: WorkerTaskRecord) -> None:
        if self.settings is None:
            return

        emit_observability_event(
            self.settings,
            "worker_log",
            "worker.task",
            trace_id=task.trace_metadata.get("trace_id"),
            request_id=task.trace_metadata.get("request_id"),
            organization_id=task.organization_id,
            project_id=task.project_id,
            actor_user_id=task.trace_metadata.get("actor_user_id"),
            document_id=task.document_id,
            strategy=task.task_type.value,
            provider="nats",
            latency_ms=_task_latency_ms(task),
            status=task.status.value,
            error_code=task.error_code,
            task_id=task.task_id,
            task_type=task.task_type.value,
            topic=task.topic,
            eval_run_id=task.eval_run_id,
            idempotency_key=task.idempotency_key,
            attempt=task.attempt,
            max_attempts=task.max_attempts,
            failure_reason=task.failure_reason,
        )

    def _read_tasks(self) -> list[WorkerTaskRecord]:
        if not self.task_path.exists():
            return []

        with self.task_path.open("r", encoding="utf-8") as file:
            raw_tasks = json.load(file)

        if not isinstance(raw_tasks, list):
            return []

        return [WorkerTaskRecord.model_validate(task) for task in raw_tasks]

    def _write_tasks(self, tasks: list[WorkerTaskRecord]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        payload = [task.model_dump(mode="json") for task in tasks]
        with self.task_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)


def task_type_for_topic(topic: str) -> WorkerTaskType:
    try:
        return TOPIC_TASK_TYPES[topic]
    except KeyError as exc:
        raise ValueError(f"Unsupported worker topic: {topic}") from exc


def idempotency_key_for_task(topic: str, payload: dict[str, object]) -> str:
    subject = (
        _optional_string(payload.get("document_id"))
        or _optional_string(payload.get("eval_run_id"))
        or "global"
    )
    project = _optional_string(payload.get("project_id")) or "no-project"
    return f"{topic}:{project}:{subject}"


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _task_latency_ms(task: WorkerTaskRecord) -> float | None:
    end_time = task.finished_at or task.updated_at
    start_time = task.started_at or task.created_at
    return round((end_time - start_time).total_seconds() * 1000, 2)
