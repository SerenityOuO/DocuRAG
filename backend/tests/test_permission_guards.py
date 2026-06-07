from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.agent import get_document_storage as get_agent_storage
from app.api.routes.auth import create_formal_token
from app.api.routes.documents import get_document_storage as get_documents_storage
from app.api.routes.rag import get_document_storage as get_rag_storage
from app.api.routes.rag import get_rag_provider
from app.core.config import get_settings
from app.main import app
from app.services.document_storage import DocumentStorage
from app.services.rag import KeywordRagProvider


@pytest.fixture
def formal_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DOCURAG_AUTH_MODE", "formal")
    monkeypatch.setenv("DOCURAG_AUTH_FORMAL_SECRET", "test-formal-secret")
    monkeypatch.setenv("DOCURAG_EMBEDDING_PROVIDER", "")
    monkeypatch.setenv("DOCURAG_RERANK_PROVIDER", "")
    get_settings.cache_clear()

    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_documents_storage] = lambda: storage
    app.dependency_overrides[get_agent_storage] = lambda: storage
    app.dependency_overrides[get_rag_storage] = lambda: storage
    app.dependency_overrides[get_rag_provider] = lambda: KeywordRagProvider()
    client = TestClient(app)

    yield client, storage

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_formal_auth_me_uses_signed_project_access_token(formal_client) -> None:
    client, _storage = formal_client

    response = client.get("/auth/me", headers=_formal_headers("analyst", ["project-a"]))
    login_response = client.post(
        "/auth/login",
        json={"username": "analyst", "password": "demo-analyst-pass"},
    )

    assert response.status_code == 200
    assert response.json()["auth_mode"] == "formal"
    assert response.json()["authenticated"] is True
    assert response.json()["user"]["role"] == "analyst"
    assert login_response.status_code == 409
    assert login_response.json()["detail"]["auth_mode"] == "formal"


@pytest.mark.parametrize("role", ["admin", "analyst"])
def test_formal_admin_and_analyst_can_upload_project_scoped_documents(
    role: str,
    formal_client,
) -> None:
    client, _storage = formal_client

    response = client.post(
        "/documents/upload",
        headers=_formal_headers(role, ["project-a"]),
        files={"file": (f"{role}.txt", b"Payment terms: Net 15", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["project_id"] == "project-a"
    assert response.json()["chunks"][0]["source_type"] == "text_upload"


def test_formal_viewer_is_forbidden_for_write_apis(formal_client) -> None:
    client, _storage = formal_client
    viewer_headers = _formal_headers("viewer", ["project-a"])

    upload_response = client.post(
        "/documents/upload",
        headers=viewer_headers,
        files={"file": ("viewer.txt", b"Viewer upload", "text/plain")},
    )
    eval_response = client.post("/eval/rag/built-in", headers=viewer_headers)
    agent_response = client.post(
        "/agent/run",
        headers=viewer_headers,
        json={"task": "ask documents", "query": "payment terms"},
    )

    for response in [upload_response, eval_response, agent_response]:
        assert response.status_code == 403
        assert response.json()["detail"]["status"] == "forbidden"
        assert response.json()["detail"]["role"] == "viewer"


def test_formal_project_boundary_filters_reads_and_blocks_cross_project_writes(
    formal_client,
) -> None:
    client, _storage = formal_client
    project_a_headers = _formal_headers("analyst", ["project-a"])
    project_b_headers = _formal_headers("analyst", ["project-b"])
    upload_response = client.post(
        "/documents/upload",
        headers=project_a_headers,
        files={"file": ("invoice.txt", b"Payment terms: Net 15", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    project_a_list = client.get("/documents", headers=project_a_headers)
    project_b_list = client.get("/documents", headers=project_b_headers)
    project_b_detail = client.get(f"/documents/{document_id}", headers=project_b_headers)
    project_b_parse = client.post(f"/documents/{document_id}/parse", headers=project_b_headers)
    project_b_download = client.get(f"/documents/{document_id}/download", headers=project_b_headers)

    assert project_a_list.status_code == 200
    assert [document["document_id"] for document in project_a_list.json()["documents"]] == [document_id]
    assert project_b_list.status_code == 200
    assert project_b_list.json()["documents"] == []
    for response in [project_b_detail, project_b_parse, project_b_download]:
        assert response.status_code == 403
        detail = response.json()["detail"]
        assert detail["status"] == "forbidden"
        assert detail["required_permission"] == "project access"
        assert document_id not in str(detail)
        assert "project-a" not in str(detail)


def test_formal_rag_query_uses_only_accessible_project_documents(formal_client) -> None:
    client, _storage = formal_client
    project_a_headers = _formal_headers("analyst", ["project-a"])
    project_b_headers = _formal_headers("viewer", ["project-b"])
    client.post(
        "/documents/upload",
        headers=project_a_headers,
        files={"file": ("invoice.txt", b"Payment terms: Net 15", "text/plain")},
    )

    project_a_response = client.post(
        "/rag/query",
        headers=project_a_headers,
        json={"query": "payment terms", "top_k": 3},
    )
    project_b_response = client.post(
        "/rag/query",
        headers=project_b_headers,
        json={"query": "payment terms", "top_k": 3},
    )

    assert project_a_response.status_code == 200
    assert project_a_response.json()["citations"]
    assert project_b_response.status_code == 200
    assert project_b_response.json()["citations"] == []
    assert project_b_response.json()["retrieved_chunks"] == []


def _formal_headers(role: str, project_ids: list[str]) -> dict[str, str]:
    token = create_formal_token(
        username=f"{role}-user",
        display_name=f"Formal {role.title()}",
        role=role,  # type: ignore[arg-type]
        organization_id="org-demo",
        project_ids=project_ids,
    )
    return {"Authorization": f"Bearer {token}"}
