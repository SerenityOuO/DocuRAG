from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.agent import get_document_storage as get_agent_storage
from app.api.routes.documents import get_document_storage as get_documents_storage
from app.api.routes.rag import get_rag_provider
from app.main import app
from app.services.document_storage import DocumentStorage
from app.services.rag import KeywordRagProvider


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    storage = DocumentStorage(tmp_path / "data")
    app.dependency_overrides[get_documents_storage] = lambda: storage
    app.dependency_overrides[get_agent_storage] = lambda: storage
    app.dependency_overrides[get_rag_provider] = lambda: KeywordRagProvider()

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def _create_parsed_invoice(client: TestClient) -> str:
    invoice_text = "\n".join(
        [
            "Fictitious Demo Invoice",
            "Invoice number: AUR-2026-051",
            "Vendor: Aurora Office Supplies Demo LLC",
            "Issue date: 2026-05-31",
            "Tax: USD 80.00",
            "Amount due: USD 1,248.50",
            "Payment terms: Net 15",
            "Line items:",
            "- 6 ergonomic chair kits at USD 149.00 each",
        ]
    )
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("mock-invoice-aurora.txt", invoice_text.encode("utf-8"), "text/plain")},
    )
    document_id = upload_response.json()["document_id"]
    ocr_response = client.post(f"/documents/{document_id}/ocr/mock")
    parser_response = client.post(f"/documents/{document_id}/parse")

    assert upload_response.status_code == 200
    assert ocr_response.status_code == 200
    assert parser_response.status_code == 200

    return document_id


def test_agent_run_returns_plan_tool_calls_answer_and_citations(client: TestClient) -> None:
    document_id = _create_parsed_invoice(client)

    response = client.post(
        "/agent/run",
        json={
            "task": "整理這份 invoice 並補充付款期限來源",
            "document_id": document_id,
            "query": "payment terms",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"].startswith("agent-run-")
    assert body["status"] == "completed"
    assert [step["tool_name"] for step in body["plan_steps"]] == [
        "get_document_fields",
        "search_documents",
        "summarize_invoice_fields",
    ]
    assert [tool_call["tool_name"] for tool_call in body["tool_calls"]] == [
        "get_document_fields",
        "search_documents",
        "summarize_invoice_fields",
    ]
    assert "Invoice AUR-2026-051 is from Aurora Office Supplies Demo LLC." in body["final_answer"]["text"]
    assert "Tool trace: get_document_fields=completed -> search_documents=completed" in body["final_answer"]["text"]
    assert body["citations"][0]["document_id"] == document_id
    assert body["citations"][0]["chunk_id"].endswith("chunk-001")
    assert body["trace"]["planner"] == "deterministic"
    assert body["trace"]["tool_policy"] == "allowlisted_read_only"
    assert body["trace"]["tool_count"] == "3"
    assert body["trace"]["fallback_count"] == "0"


def test_agent_run_lookup_returns_saved_run(client: TestClient) -> None:
    document_id = _create_parsed_invoice(client)
    run_response = client.post(
        "/agent/run",
        json={
            "task": "summarize invoice fields",
            "document_id": document_id,
            "query": "payment terms",
        },
    )
    run_id = run_response.json()["run_id"]

    response = client.get(f"/agent/runs/{run_id}")

    assert response.status_code == 200
    assert response.json()["run_id"] == run_id
    assert response.json()["status"] == "completed"


def test_agent_run_returns_failed_step_when_parser_result_is_missing(client: TestClient) -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("invoice.txt", b"Invoice number: AUR-2026-051", "text/plain")},
    )
    document_id = upload_response.json()["document_id"]
    client.post(f"/documents/{document_id}/ocr/mock")

    response = client.post(
        "/agent/run",
        json={"task": "summarize invoice fields", "document_id": document_id, "query": "payment terms"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["plan_steps"][0]["tool_name"] == "get_document_fields"
    assert body["plan_steps"][0]["status"] == "failed"
    assert body["plan_steps"][0]["fallback_reason"] == "parser_result_missing"
    assert body["final_answer"]["fallback_reason"] == "parser_result_missing"


def test_agent_run_completes_invoice_summary_with_search_fallback(client: TestClient) -> None:
    document_id = _create_parsed_invoice(client)

    response = client.post(
        "/agent/run",
        json={
            "task": "summarize invoice fields",
            "document_id": document_id,
            "query": "unmatched phrase",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["plan_steps"][1]["tool_name"] == "search_documents"
    assert body["plan_steps"][1]["status"] == "failed"
    assert body["plan_steps"][1]["fallback_reason"] == "no_retrieved_chunks"
    assert body["final_answer"]["fallback_reason"] == "no_retrieved_chunks"
    assert "Invoice AUR-2026-051 is from Aurora Office Supplies Demo LLC." in body["final_answer"]["text"]
    assert body["citations"] == []
    assert body["trace"]["fallback_count"] == "1"


def test_agent_run_returns_failed_state_for_invalid_document(client: TestClient) -> None:
    response = client.post(
        "/agent/run",
        json={"task": "summarize invoice fields", "document_id": "missing-doc", "query": "payment terms"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["plan_steps"][0]["tool_name"] == "get_document_fields"
    assert body["plan_steps"][0]["fallback_reason"] == "document_not_found"
    assert body["final_answer"]["fallback_reason"] == "document_not_found"


def test_agent_run_lookup_returns_404_for_unknown_run(client: TestClient) -> None:
    response = client.get("/agent/runs/not-found")

    assert response.status_code == 404
    assert response.json()["detail"] == "Agent run not found"
