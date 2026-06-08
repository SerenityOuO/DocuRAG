import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.api.routes.documents import get_document_storage as get_documents_storage
from app.api.routes.rag import get_document_storage as get_rag_storage
from app.api.routes.rag import get_rag_provider
from app.core.config import Settings, get_settings
from app.main import app
from app.services.document_storage import DocumentStorage
from app.services.observability import (
    REQUIRED_OBSERVABILITY_FIELDS,
    build_observability_event,
    emit_observability_event,
)
from app.services.rag import KeywordRagProvider
from app.services.task_status import TaskStatusStore
from app.schemas.tasks import WorkerTaskStatus


@pytest.fixture(autouse=True)
def clean_app_state() -> None:
    app.dependency_overrides.clear()
    get_settings.cache_clear()
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_observability_event_schema_keeps_required_fields(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path, observability_log_path=tmp_path / "events.jsonl")

    event = build_observability_event(
        settings,
        "api_request",
        "api.request",
        trace_id="trace-001",
        request_id="request-001",
        latency_ms=12.34,
        status="ok",
    )

    for field_name in REQUIRED_OBSERVABILITY_FIELDS:
        assert field_name in event

    assert event["schema_version"] == "docurag_observability_v1"
    assert event["event_type"] == "api_request"
    assert event["event_name"] == "api.request"
    assert event["trace_id"] == "trace-001"
    assert event["request_id"] == "request-001"
    assert event["organization_id"] is None
    assert event["latency_ms"] == 12.34
    assert event["status"] == "ok"


def test_emit_observability_event_is_disabled_or_best_effort(tmp_path: Path) -> None:
    disabled = Settings(data_dir=tmp_path, observability_log_path=None)
    blocked = Settings(data_dir=tmp_path, observability_log_path=tmp_path)

    assert emit_observability_event(disabled, "api_request", "api.request", status="ok") is None
    assert emit_observability_event(blocked, "api_request", "api.request", status="ok") is None


def test_rag_query_exports_api_and_rag_observability_events(
    monkeypatch,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "observability" / "events.jsonl"
    monkeypatch.setenv("DOCURAG_OBSERVABILITY_LOG_PATH", str(log_path))
    monkeypatch.setenv("DOCURAG_LLM_PROVIDER", "")
    get_settings.cache_clear()

    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_documents_storage] = lambda: storage
    app.dependency_overrides[get_rag_storage] = lambda: storage
    app.dependency_overrides[get_rag_provider] = lambda: KeywordRagProvider()
    client = TestClient(app)

    upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "invoice.txt",
                b"Invoice number: AUR-2026-051\nPayment terms: Net 15",
                "text/plain",
            )
        },
        headers={"X-Request-ID": "request-rag-001", "X-Trace-ID": "trace-rag-001"},
    )
    assert upload.status_code == 200

    response = client.post(
        "/rag/query",
        json={"query": "payment terms", "top_k": 3},
        headers={"X-Request-ID": "request-rag-002", "X-Trace-ID": "trace-rag-002"},
    )

    assert response.status_code == 200
    events = _read_events(log_path)
    rag_event = _event(events, "rag_trace")
    api_event = next(event for event in events if event["event_type"] == "api_request" and event.get("route") == "/rag/query")

    assert api_event["request_id"] == "request-rag-002"
    assert api_event["trace_id"] == "trace-rag-002"
    assert api_event["status"] == "ok"
    assert rag_event["request_id"] == "request-rag-002"
    assert rag_event["trace_id"] == "trace-rag-002"
    assert rag_event["strategy"] == "hybrid_rerank"
    assert rag_event["provider"] == "keyword"
    assert rag_event["retrieved_chunk_count"] == 1
    assert rag_event["citation_count"] == 1
    assert rag_event["fallback_count"] == 0
    assert "query" not in rag_event


def test_eval_endpoint_exports_metrics_observability_event(
    monkeypatch,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "observability" / "events.jsonl"
    monkeypatch.setenv("DOCURAG_OBSERVABILITY_LOG_PATH", str(log_path))
    monkeypatch.setenv("DOCURAG_EMBEDDING_PROVIDER", "")
    monkeypatch.setenv("DOCURAG_RERANK_PROVIDER", "")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/eval/rag/built-in",
        headers={"X-Request-ID": "request-eval-001", "X-Trace-ID": "trace-eval-001"},
    )

    assert response.status_code == 200
    event = _event(_read_events(log_path), "eval_metrics")
    assert event["event_name"] == "eval.run"
    assert event["request_id"] == "request-eval-001"
    assert event["trace_id"] == "trace-eval-001"
    assert event["strategy"] == "hybrid_rerank"
    assert event["provider"] == "hybrid_rerank"
    assert event["hit_rate_at_k"] == 1.0
    assert event["mrr_at_k"] == 1.0
    assert event["fallback_count"] == 10


def test_worker_task_status_exports_observability_events(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        observability_log_path=tmp_path / "observability" / "events.jsonl",
    )
    store = TaskStatusStore(settings.data_dir, settings=settings)

    task = store.create_task(
        "document.ocr.requested",
        {
            "organization_id": "org-001",
            "project_id": "project-001",
            "document_id": "doc-001",
        },
    )
    store.update_task(
        task.task_id,
        WorkerTaskStatus.FAILED,
        failure_reason="provider unavailable",
        error_code="ocr_unavailable",
    )

    events = _read_events(settings.observability_log_path)
    queued = next(event for event in events if event["event_type"] == "worker_log" and event["status"] == "queued")
    failed = next(event for event in events if event["event_type"] == "worker_log" and event["status"] == "failed")

    assert queued["organization_id"] == "org-001"
    assert queued["project_id"] == "project-001"
    assert queued["document_id"] == "doc-001"
    assert queued["provider"] == "nats"
    assert queued["strategy"] == "ocr"
    assert failed["error_code"] == "ocr_unavailable"
    assert failed["failure_reason"] == "provider unavailable"


def _read_events(log_path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _event(events: list[dict[str, object]], event_type: str) -> dict[str, object]:
    return next(event for event in events if event["event_type"] == event_type)
