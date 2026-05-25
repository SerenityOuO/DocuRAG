from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import get_document_storage
from app.core.config import get_settings
from app.main import app
from app.services.document_storage import DocumentStorage


@pytest.fixture(autouse=True)
def demo_auth_mode(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DOCURAG_AUTH_MODE", "demo")
    monkeypatch.setenv("DOCURAG_AUTH_DEMO_SECRET", "test-demo-secret")
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


def test_demo_login_me_and_logout() -> None:
    client = TestClient(app)

    login_response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "demo-admin-pass"},
    )

    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["auth_mode"] == "demo"
    assert login_body["token_type"] == "bearer"
    assert login_body["access_token"]
    assert login_body["user"] == {
        "username": "admin",
        "display_name": "Demo Admin",
        "role": "admin",
    }
    assert "password" not in login_body

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login_body['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["authenticated"] is True
    assert me_response.json()["user"]["role"] == "admin"

    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.json() == {"auth_mode": "demo", "status": "logged_out"}


def test_auth_me_reports_disabled_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCURAG_AUTH_MODE", "disabled")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "auth_mode": "disabled",
        "authenticated": False,
        "user": None,
    }


def test_demo_write_api_requires_token(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_document_storage] = lambda: storage
    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        files={"file": ("invoice.txt", b"Invoice number: AUR-2026-051", "text/plain")},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Demo auth token is required."


def test_viewer_role_cannot_use_ingestion_apis(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_document_storage] = lambda: storage
    client = TestClient(app)
    admin_headers = _login_headers(client, "admin", "demo-admin-pass")
    viewer_headers = _login_headers(client, "viewer", "demo-viewer-pass")
    upload_response = client.post(
        "/documents/upload",
        headers=admin_headers,
        files={"file": ("invoice.txt", b"Invoice number: AUR-2026-051", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    upload_forbidden = client.post(
        "/documents/upload",
        headers=viewer_headers,
        files={"file": ("viewer.txt", b"Viewer upload", "text/plain")},
    )
    mock_ocr_forbidden = client.post(f"/documents/{document_id}/ocr/mock", headers=viewer_headers)
    ocr_forbidden = client.post(f"/documents/{document_id}/ocr", headers=viewer_headers)
    parse_forbidden = client.post(f"/documents/{document_id}/parse", headers=viewer_headers)
    index_forbidden = client.post(f"/documents/{document_id}/index/vector", headers=viewer_headers)

    for response in [
        upload_forbidden,
        mock_ocr_forbidden,
        ocr_forbidden,
        parse_forbidden,
        index_forbidden,
    ]:
        assert response.status_code == 403
        assert response.json()["detail"]["status"] == "forbidden"
        assert response.json()["detail"]["role"] == "viewer"


def test_download_requires_login_but_allows_viewer(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_document_storage] = lambda: storage
    client = TestClient(app)
    admin_headers = _login_headers(client, "admin", "demo-admin-pass")
    viewer_headers = _login_headers(client, "viewer", "demo-viewer-pass")
    upload_response = client.post(
        "/documents/upload",
        headers=admin_headers,
        files={"file": ("invoice.txt", b"Invoice number: AUR-2026-051", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]

    unauthenticated_download = client.get(f"/documents/{document_id}/download")
    viewer_download = client.get(f"/documents/{document_id}/download", headers=viewer_headers)

    assert unauthenticated_download.status_code == 401
    assert unauthenticated_download.json()["detail"] == "Demo auth token is required."
    assert viewer_download.status_code == 200
    assert viewer_download.content == b"Invoice number: AUR-2026-051"


@pytest.mark.parametrize(
    ("username", "password", "expected_role"),
    [
        ("admin", "demo-admin-pass", "admin"),
        ("analyst", "demo-analyst-pass", "analyst"),
    ],
)
def test_admin_and_analyst_can_upload_documents(
    username: str,
    password: str,
    expected_role: str,
    tmp_path: Path,
) -> None:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_document_storage] = lambda: storage
    client = TestClient(app)
    headers = _login_headers(client, username, password)

    response = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("invoice.txt", b"Invoice number: AUR-2026-051", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["chunks"][0]["source_type"] == "text_upload"
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.json()["user"]["role"] == expected_role
