from fastapi.testclient import TestClient
import pytest

from app.core.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def clean_settings() -> None:
    get_settings.cache_clear()
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def _login_headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_built_in_rag_eval_endpoint_runs_hybrid_rerank_with_demo_safe_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DOCURAG_EMBEDDING_PROVIDER", "")
    monkeypatch.setenv("DOCURAG_RERANK_PROVIDER", "")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post("/eval/rag/built-in")

    assert response.status_code == 200
    body = response.json()
    assert body["strategy"] == "hybrid_rerank"
    assert body["dataset_name"] == "zh_invoice_hybrid_rerank_v1"
    assert body["case_count"] == 10
    assert body["summary"]["case_count"] == 10
    assert body["summary"]["hit_rate_at_k"] == 1.0
    assert body["summary"]["mrr_at_k"] == 1.0
    assert body["summary"]["failure_count"] == 0
    assert body["summary"]["fallback_count"] == 10
    assert body["summary"]["average_latency_ms"] >= 0
    assert body["environment"]["retrieval_provider"] == "hybrid_rerank"
    assert body["environment"]["dataset_name"] == "zh_invoice_hybrid_rerank_v1"
    assert body["environment"]["document_fixture_count"] == 10
    assert body["failed_cases"] == []
    assert len(body["fallback_cases"]) == 10
    assert all(case["fallback_reasons"] for case in body["fallback_cases"])


def test_built_in_rag_eval_endpoint_blocks_viewer_in_demo_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DOCURAG_AUTH_MODE", "demo")
    monkeypatch.setenv("DOCURAG_AUTH_DEMO_SECRET", "test-demo-secret")
    monkeypatch.setenv("DOCURAG_EMBEDDING_PROVIDER", "")
    monkeypatch.setenv("DOCURAG_RERANK_PROVIDER", "")
    get_settings.cache_clear()
    client = TestClient(app)
    viewer_headers = _login_headers(client, "viewer", "demo-viewer-pass")

    response = client.post("/eval/rag/built-in", headers=viewer_headers)

    assert response.status_code == 403
    assert response.json()["detail"]["status"] == "forbidden"
    assert response.json()["detail"]["role"] == "viewer"


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("admin", "demo-admin-pass"),
        ("analyst", "demo-analyst-pass"),
    ],
)
def test_built_in_rag_eval_endpoint_allows_admin_and_analyst_in_demo_auth(
    username: str,
    password: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DOCURAG_AUTH_MODE", "demo")
    monkeypatch.setenv("DOCURAG_AUTH_DEMO_SECRET", "test-demo-secret")
    monkeypatch.setenv("DOCURAG_EMBEDDING_PROVIDER", "")
    monkeypatch.setenv("DOCURAG_RERANK_PROVIDER", "")
    get_settings.cache_clear()
    client = TestClient(app)
    headers = _login_headers(client, username, password)

    response = client.post("/eval/rag/built-in", headers=headers)

    assert response.status_code == 200
    assert response.json()["summary"]["case_count"] == 10
