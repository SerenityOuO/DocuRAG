from fastapi.testclient import TestClient

from app.main import app


def test_upload_document_returns_uploaded_metadata() -> None:
    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        files={"file": ("invoice.pdf", b"sample document", "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["document_id"]
    assert "project_id" in body
    assert body["filename"] == "invoice.pdf"
    assert body["file_type"] == "pdf"
    assert body["content_type"] == "application/pdf"
    assert body["size"] == len(b"sample document")
    assert body["status"] == "uploaded"
