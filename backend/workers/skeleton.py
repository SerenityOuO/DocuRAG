from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import shutil

from app.core.config import Settings
from app.schemas.tasks import WorkerTaskRecord, WorkerTaskStatus
from app.services.nats_runtime import NatsMessage, NatsOperationResult, NatsRuntime, create_nats_runtime
from app.services.task_status import TOPIC_TASK_TYPES, TaskStatusStore


class WorkerSkeleton:
    def __init__(self, task_store: TaskStatusStore) -> None:
        self.task_store = task_store

    async def subscribe(self, runtime: NatsRuntime) -> list[NatsOperationResult]:
        results = []
        for topic in TOPIC_TASK_TYPES:
            results.append(await runtime.subscribe(topic, self.handle_message))
        return results

    async def enqueue_task(
        self,
        runtime: NatsRuntime,
        topic: str,
        payload: dict[str, object],
    ) -> tuple[WorkerTaskRecord, NatsOperationResult]:
        task = self.task_store.create_task(topic, payload)
        publish_payload = {
            **payload,
            "task_id": task.task_id,
            "idempotency_key": task.idempotency_key,
        }
        result = await runtime.publish(topic, publish_payload)
        if result.status in {"disabled", "unavailable"}:
            self.task_store.update_task(
                task.task_id,
                WorkerTaskStatus.FAILED,
                error_code="nats_unavailable",
                failure_reason=result.detail or f"NATS publish {result.status}.",
                trace_metadata={
                    "publish_status": result.status,
                },
            )
        return task, result

    async def handle_message(self, message: NatsMessage) -> None:
        task_id = str(message.payload.get("task_id") or "").strip()
        if not task_id:
            return

        running = self.task_store.update_task(
            task_id,
            WorkerTaskStatus.RUNNING,
            trace_metadata={
                "worker_handler": "placeholder",
                "topic": message.topic,
            },
        )
        if running is None:
            return

        self.task_store.update_task(
            task_id,
            WorkerTaskStatus.SUCCEEDED,
            trace_metadata={
                "placeholder_result": "acknowledged",
                "topic": message.topic,
            },
        )


async def run_smoke(data_dir: Path) -> WorkerTaskRecord:
    if data_dir.exists():
        shutil.rmtree(data_dir)
    task_store = TaskStatusStore(data_dir)
    runtime = await create_nats_runtime(Settings(data_dir=data_dir, nats_url="memory://"))
    worker = WorkerSkeleton(task_store)
    await worker.subscribe(runtime)
    task, publish_result = await worker.enqueue_task(
        runtime,
        "document.ocr.requested",
        {
            "document_id": "smoke-document",
            "project_id": "smoke-project",
            "organization_id": "smoke-org",
        },
    )
    if publish_result.status != "published":
        raise RuntimeError(f"NATS smoke publish failed: {publish_result.status} {publish_result.detail}")

    final_task = task_store.get_task(task.task_id)
    if final_task is None or final_task.status != WorkerTaskStatus.SUCCEEDED:
        raise RuntimeError("NATS smoke worker did not mark the task as succeeded.")

    await runtime.close()
    return final_task


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Phase 33 NATS worker skeleton smoke check.")
    parser.add_argument("--smoke", action="store_true", help="Run an in-memory publish / consume smoke check.")
    parser.add_argument("--data-dir", default="../.tmp/nats-worker-smoke", help="Smoke task status data directory.")
    args = parser.parse_args()

    if not args.smoke:
        parser.error("--smoke is required for this skeleton entrypoint")

    task = asyncio.run(run_smoke(Path(args.data_dir)))
    print(f"NATS worker smoke succeeded: task_id={task.task_id} status={task.status}")


if __name__ == "__main__":
    main()
