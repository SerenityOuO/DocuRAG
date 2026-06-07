Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendRoot ".venv/Scripts/python.exe"
$smokeDataDir = Join-Path ([System.IO.Path]::GetTempPath()) "docurag-worker-demo-smoke"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Backend virtual environment was not found. Run scripts/test-backend.ps1 first."
}

$env:DOCURAG_WORKER_SMOKE_DATA_DIR = $smokeDataDir

$smokeCode = @'
import asyncio
import os
from pathlib import Path

from fastapi.testclient import TestClient

data_dir = Path(os.environ["DOCURAG_WORKER_SMOKE_DATA_DIR"])
data_dir.mkdir(parents=True, exist_ok=True)

os.environ["DOCURAG_DATA_DIR"] = str(data_dir)
os.environ["DOCURAG_NATS_URL"] = "memory://"
os.environ["DOCURAG_REDIS_URL"] = "redis://worker-demo-smoke/0"

from app.core.config import Settings, get_settings
from app.main import app
from app.schemas.auth import AuthUser
from app.schemas.rag import RagQueryResponse
from app.schemas.tasks import WorkerTaskStatus
from app.services.nats_runtime import create_nats_runtime
from app.services.redis_runtime import RedisRuntime
from app.services.task_status import TaskStatusStore
from workers.skeleton import WorkerSkeleton


class SmokeRedisClient:
    def __init__(self):
        self.values = {}
        self.ttls = {}

    def ping(self):
        return True

    def setex(self, key, ttl, value):
        self.values[key] = value
        self.ttls[key] = ttl

    def get(self, key):
        value = self.values.get(key)
        return value if isinstance(value, str) else None

    def incr(self, key):
        value = int(self.values.get(key, 0)) + 1
        self.values[key] = value
        return value

    def expire(self, key, ttl):
        self.ttls[key] = ttl

    def ttl(self, key):
        return self.ttls.get(key, -1)


def assert_condition(condition, message):
    if not condition:
        raise RuntimeError(message)


def run_redis_smoke(settings):
    redis_runtime = RedisRuntime(settings, client=SmokeRedisClient())
    assert_condition(redis_runtime.health().status == "ok", "Redis smoke health did not return ok.")

    user = AuthUser(username="admin", display_name="Demo Admin", role="admin")
    assert_condition(redis_runtime.cache_session("worker-smoke-token", user).status == "stored", "Redis session cache failed.")

    response = RagQueryResponse(answer="cached worker smoke answer", citations=[], retrieved_chunks=[])
    assert_condition(redis_runtime.set_query_cache("worker-smoke-query", response).status == "stored", "Redis query cache write failed.")
    cache_read = redis_runtime.get_query_cache("worker-smoke-query")
    assert_condition(cache_read.status == "hit" and cache_read.response == response, "Redis query cache read failed.")

    first = redis_runtime.check_rate_limit("worker-smoke", limit=1, window_seconds=60)
    second = redis_runtime.check_rate_limit("worker-smoke", limit=1, window_seconds=60)
    assert_condition(first.allowed and first.status == "ok", "Redis rate limit first request failed.")
    assert_condition((not second.allowed) and second.status == "limited", "Redis rate limit did not block over-limit request.")


async def run_nats_worker_smoke(settings):
    task_store = TaskStatusStore(settings.data_dir)
    runtime = await create_nats_runtime(settings)
    worker = WorkerSkeleton(task_store)

    try:
        subscribe_results = await worker.subscribe(runtime)
        assert_condition(all(result.status == "subscribed" for result in subscribe_results), "NATS subscribe smoke failed.")

        task, publish_result = await worker.enqueue_task(
            runtime,
            "document.ocr.requested",
            {"document_id": "worker-demo-document", "project_id": "project-demo"},
        )
        assert_condition(publish_result.status == "published", "NATS publish smoke failed.")

        stored = task_store.get_task(task.task_id)
        assert_condition(stored is not None, "Task status was not stored.")
        assert_condition(stored.status == WorkerTaskStatus.SUCCEEDED, f"Task status was {stored.status}.")
        return stored.task_id
    finally:
        await runtime.close()


settings = Settings(data_dir=data_dir, redis_url="redis://worker-demo-smoke/0", nats_url="memory://")
run_redis_smoke(settings)
task_id = asyncio.run(run_nats_worker_smoke(settings))

get_settings.cache_clear()
client = TestClient(app)
health = client.get("/health")
assert_condition(health.status_code == 200, "Health endpoint failed.")
health_body = health.json()
assert_condition(health_body["version"] == "0.33.0", f"Expected health version 0.33.0, got {health_body['version']}.")
assert_condition(health_body["status"] == "ok", "Health status was not ok.")

tasks = client.get("/tasks")
assert_condition(tasks.status_code == 200, "Task list endpoint failed.")
task_ids = {task["task_id"] for task in tasks.json()["tasks"]}
assert_condition(task_id in task_ids, "Task list did not include worker smoke task.")

task_detail = client.get(f"/tasks/{task_id}")
assert_condition(task_detail.status_code == 200, "Task detail endpoint failed.")
assert_condition(task_detail.json()["status"] == "succeeded", "Task detail was not succeeded.")

print(f"Worker demo smoke succeeded: version={health_body['version']} task_id={task_id} redis=ok nats=memory task_status=succeeded")
'@

Push-Location $backendRoot
try {
    $smokeCode | & $venvPython -
    if ($LASTEXITCODE -ne 0) {
        throw "Worker demo smoke failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
    Remove-Item Env:\DOCURAG_WORKER_SMOKE_DATA_DIR -ErrorAction SilentlyContinue
}
