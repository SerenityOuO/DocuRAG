from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes.agent import get_agent_planner
from app.api.routes.agent import get_document_storage as get_agent_storage
from app.api.routes.documents import get_document_storage as get_documents_storage
from app.api.routes.rag import get_rag_provider
from app.main import app
from app.schemas.agent import AgentRunRequest
from app.services.agent import AgentService
from app.services.agent_planner import LlmAgentPlanner
from app.services.agent_tools import AgentToolService
from app.services.document_storage import DocumentStorage
from app.services.llm import LlmGeneration, LlmHealth, LlmProviderError
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
    parser_response = client.post(f"/documents/{document_id}/parse")

    assert upload_response.status_code == 200
    assert upload_response.json()["ocr"]["status"] == "pending"
    assert upload_response.json()["chunks"][0]["source_type"] == "text_upload"
    assert parser_response.status_code == 200

    return document_id


class StubPlannerLlmProvider:
    name = "stub_planner_llm"

    def __init__(self, response_text: str | None = None, error: Exception | None = None) -> None:
        self.response_text = response_text
        self.error = error
        self.prompt = ""
        self.system = ""

    def generate(self, prompt: str, system: str | None = None) -> LlmGeneration:
        self.prompt = prompt
        self.system = system or ""
        if self.error is not None:
            raise self.error
        return LlmGeneration(
            text=self.response_text or "",
            model="stub-planner",
            prompt_tokens=12,
            completion_tokens=8,
            total_tokens=20,
            provider_latency_ms=1.5,
        )

    def check_health(self) -> LlmHealth:
        return LlmHealth(provider=self.name, enabled=True, available=True, message="ok")


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
    assert body["citations"][0]["source_type"] == "text_upload"
    assert body["trace"]["planner"] == "deterministic"
    assert body["trace"]["tool_policy"] == "allowlisted_read_only"
    assert body["trace"]["permission_decision"] == "allowed"
    assert body["trace"]["permission_checked_tool_count"] == "3"
    assert body["trace"]["tool_count"] == "3"
    assert body["trace"]["fallback_count"] == "2"
    for tool_call in body["tool_calls"]:
        metadata = tool_call["trace_metadata"]
        assert metadata["tool_tier"] == "read-only"
        assert metadata["permission_decision"] == "allowed"
        assert metadata["required_roles"] == "admin,analyst"
        assert metadata["side_effect_policy"] == "no_side_effects"
        assert metadata["human_confirmation_required"] == "not_required"
    assert body["tool_calls"][0]["observation"]["fallback_reason"] == "unsupported_file"
    assert body["tool_calls"][2]["observation"]["fallback_reason"] == "unsupported_file"


def test_agent_run_uses_llm_planner_when_enabled(client: TestClient) -> None:
    planner_llm = StubPlannerLlmProvider(
        response_text=(
            '{"route":"invoice_summary","steps":['
            '{"tool_name":"get_document_fields"},'
            '{"tool_name":"search_documents"},'
            '{"tool_name":"summarize_invoice_fields"}]}'
        )
    )
    app.dependency_overrides[get_agent_planner] = lambda: LlmAgentPlanner(planner_llm)
    document_id = _create_parsed_invoice(client)

    response = client.post(
        "/agent/run",
        json={
            "task": "整理這份 invoice 並補充付款期限來源",
            "document_id": document_id,
            "query": "payment terms",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert [tool_call["tool_name"] for tool_call in body["tool_calls"]] == [
        "get_document_fields",
        "search_documents",
        "summarize_invoice_fields",
    ]
    assert body["trace"]["planner"] == "llm_planner"
    assert body["trace"]["planner_attempted_provider"] == "llm_planner"
    assert body["trace"]["planner_status"] == "completed"
    assert body["trace"]["plan_validation_status"] == "valid"
    assert body["trace"]["planned_tools"] == "get_document_fields,search_documents,summarize_invoice_fields"
    assert body["trace"]["planner_model"] == "stub-planner"
    assert '"allowed_tools"' in planner_llm.prompt


def test_agent_run_falls_back_to_deterministic_planner_on_llm_timeout(client: TestClient) -> None:
    planner_llm = StubPlannerLlmProvider(
        error=LlmProviderError("OpenAI-compatible request timed out after 1.0s at http://planner.")
    )
    app.dependency_overrides[get_agent_planner] = lambda: LlmAgentPlanner(planner_llm)
    document_id = _create_parsed_invoice(client)

    response = client.post(
        "/agent/run",
        json={
            "task": "summarize invoice fields",
            "document_id": document_id,
            "query": "payment terms",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["trace"]["planner"] == "deterministic"
    assert body["trace"]["planner_attempted_provider"] == "llm_planner"
    assert body["trace"]["planner_status"] == "fallback"
    assert body["trace"]["plan_validation_status"] == "timeout"
    assert body["trace"]["planner_fallback_reason"] == "llm_planner_timeout"
    assert [tool_call["tool_name"] for tool_call in body["tool_calls"]] == [
        "get_document_fields",
        "search_documents",
        "summarize_invoice_fields",
    ]


def test_agent_run_falls_back_without_executing_invalid_llm_plan(client: TestClient) -> None:
    planner_llm = StubPlannerLlmProvider(
        response_text='{"route":"invoice_summary","steps":[{"tool_name":"delete_project"}]}'
    )
    app.dependency_overrides[get_agent_planner] = lambda: LlmAgentPlanner(planner_llm)
    document_id = _create_parsed_invoice(client)

    response = client.post(
        "/agent/run",
        json={
            "task": "summarize invoice fields",
            "document_id": document_id,
            "query": "payment terms",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["trace"]["planner"] == "deterministic"
    assert body["trace"]["planner_status"] == "fallback"
    assert body["trace"]["plan_validation_status"] == "invalid"
    assert body["trace"]["permission_decision"] == "allowed"
    assert body["trace"]["planner_fallback_reason"].startswith("llm_planner_invalid_plan")
    assert [tool_call["tool_name"] for tool_call in body["tool_calls"]] == [
        "get_document_fields",
        "search_documents",
        "summarize_invoice_fields",
    ]
    assert "delete_project" not in {tool_call["tool_name"] for tool_call in body["tool_calls"]}


def test_agent_run_blocks_forbidden_tool_execution_for_viewer_role(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    service = AgentService(
        storage,
        AgentToolService(storage, rag_provider=KeywordRagProvider()),
    )

    result = service.run(
        AgentRunRequest(task="ask documents", query="payment terms"),
        project_id="project-a",
        role="viewer",
    )

    assert result.status == "failed"
    assert result.tool_calls == []
    assert result.final_answer.fallback_reason == "tool_permission_forbidden"
    assert result.plan_steps[0].tool_name == "search_documents"
    assert result.plan_steps[0].fallback_reason == "tool_permission_forbidden"
    assert result.trace["permission_decision"] == "forbidden"
    assert result.trace["permission_denied_tool"] == "search_documents"
    assert result.trace["permission_fallback_reason"] == "tool_permission_forbidden"
    assert result.trace["role"] == "viewer"


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
    assert body["trace"]["fallback_count"] == "3"
    assert body["tool_calls"][0]["observation"]["fallback_reason"] == "unsupported_file"
    assert body["tool_calls"][1]["observation"]["fallback_reason"] == "no_retrieved_chunks"
    assert body["tool_calls"][2]["observation"]["fallback_reason"] == "unsupported_file"


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
