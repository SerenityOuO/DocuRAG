from fastapi.testclient import TestClient
import pytest

from app.core.config import get_settings
from app.api.routes.evaluation import get_document_storage as get_eval_document_storage
from app.main import app
from app.services.document_storage import DocumentStorage


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


def _eval_client(tmp_path) -> TestClient:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_eval_document_storage] = lambda: storage
    return TestClient(app)


def test_eval_dataset_api_manages_dataset_and_items(tmp_path) -> None:
    client = _eval_client(tmp_path)

    dataset_response = client.post(
        "/eval/datasets",
        json={
            "name": "Invoice retrieval quality",
            "description": "Demo-safe eval dataset",
        },
    )

    assert dataset_response.status_code == 200
    dataset = dataset_response.json()
    assert dataset["name"] == "Invoice retrieval quality"
    assert dataset["schema_version"] == "eval_dataset_v1"
    assert dataset["item_count"] == 0

    dataset_id = dataset["dataset_id"]
    list_response = client.get("/eval/datasets")

    assert list_response.status_code == 200
    assert [item["dataset_id"] for item in list_response.json()["datasets"]] == [dataset_id]

    update_response = client.patch(
        f"/eval/datasets/{dataset_id}",
        json={"name": "Invoice retrieval quality v2"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Invoice retrieval quality v2"

    item_response = client.post(
        f"/eval/datasets/{dataset_id}/items",
        json={
            "query": "付款期限是什麼？",
            "expected_terms": ["Net 15", "payment terms"],
            "expected_document_ids": ["doc-001"],
            "expected_chunk_ids": ["doc-001-chunk-001"],
            "tags": ["invoice"],
            "notes": "demo-safe item",
        },
    )

    assert item_response.status_code == 200
    item = item_response.json()
    assert item["query"] == "付款期限是什麼？"
    assert item["expected_terms"] == ["Net 15", "payment terms"]

    detail_response = client.get(f"/eval/datasets/{dataset_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["dataset"]["item_count"] == 1
    assert detail_response.json()["items"][0]["item_id"] == item["item_id"]

    item_update_response = client.patch(
        f"/eval/datasets/{dataset_id}/items/{item['item_id']}",
        json={"query": "更新後的付款期限問題", "tags": ["invoice", "terms"]},
    )

    assert item_update_response.status_code == 200
    assert item_update_response.json()["query"] == "更新後的付款期限問題"
    assert item_update_response.json()["tags"] == ["invoice", "terms"]

    item_delete_response = client.delete(f"/eval/datasets/{dataset_id}/items/{item['item_id']}")

    assert item_delete_response.status_code == 200
    assert item_delete_response.json() == {
        "status": "deleted",
        "dataset_id": dataset_id,
        "item_id": item["item_id"],
    }
    assert client.get(f"/eval/datasets/{dataset_id}/items").json()["items"] == []

    dataset_delete_response = client.delete(f"/eval/datasets/{dataset_id}")

    assert dataset_delete_response.status_code == 200
    assert dataset_delete_response.json() == {
        "status": "deleted",
        "dataset_id": dataset_id,
        "item_id": None,
    }
    assert client.get("/eval/datasets").json()["datasets"] == []


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


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("admin", "demo-admin-pass"),
        ("analyst", "demo-analyst-pass"),
    ],
)
def test_eval_dataset_api_allows_admin_and_analyst_in_demo_auth(
    username: str,
    password: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("DOCURAG_AUTH_MODE", "demo")
    monkeypatch.setenv("DOCURAG_AUTH_DEMO_SECRET", "test-demo-secret")
    get_settings.cache_clear()
    client = _eval_client(tmp_path)
    headers = _login_headers(client, username, password)

    response = client.post(
        "/eval/datasets",
        headers=headers,
        json={"name": "Invoice eval dataset"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Invoice eval dataset"


def test_eval_dataset_api_blocks_viewer_writes_in_demo_auth(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("DOCURAG_AUTH_MODE", "demo")
    monkeypatch.setenv("DOCURAG_AUTH_DEMO_SECRET", "test-demo-secret")
    get_settings.cache_clear()
    client = _eval_client(tmp_path)
    viewer_headers = _login_headers(client, "viewer", "demo-viewer-pass")

    response = client.post(
        "/eval/datasets",
        headers=viewer_headers,
        json={"name": "Viewer dataset"},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["status"] == "forbidden"
    assert response.json()["detail"]["role"] == "viewer"
