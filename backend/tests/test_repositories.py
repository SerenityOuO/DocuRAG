from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest

from app.core.config import Settings
from app.repositories.document_metadata import (
    LocalJsonDocumentRepository,
    POSTGRES_SCHEMA_STATEMENTS,
    PostgresDocumentRepository,
    create_document_repository,
    create_document_storage,
)
from app.schemas.agent import AgentFinalAnswer, AgentRun, AgentRunStatus, AgentStep
from app.schemas.documents import (
    DocumentChunk,
    DocumentFields,
    DocumentMetadata,
    DocumentStatus,
    ExtractedField,
    ParserResult,
    ParserStatus,
    ProcessingJob,
    ProcessingJobType,
    ProcessingStepStatus,
)
from app.schemas.evaluation import EvalDataset, EvalItem


class FakeCursor:
    def __init__(self, rows: list[tuple[dict[str, Any]]]) -> None:
        self.rows = rows

    def fetchall(self) -> list[tuple[dict[str, Any]]]:
        return self.rows


class FakePostgresConnection:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.tables: dict[str, dict[str, dict[str, Any]]] = {
            "documents": {},
            "document_chunks": {},
            "extracted_fields": {},
            "processing_jobs": {},
            "eval_datasets": {},
            "eval_items": {},
            "eval_runs": {},
            "agent_runs": {},
            "agent_steps": {},
            "agent_tool_calls": {},
        }

    def __enter__(self):
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, sql: str, params: tuple[object, ...] | None = None) -> FakeCursor:
        normalized = " ".join(sql.casefold().split())
        self.statements.append(normalized)

        if normalized.startswith("create table") or normalized.startswith("create index"):
            return FakeCursor([])

        if normalized.startswith("insert into documents"):
            assert params is not None
            self.tables["documents"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into document_chunks"):
            assert params is not None
            self.tables["document_chunks"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into extracted_fields"):
            assert params is not None
            self.tables["extracted_fields"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into processing_jobs"):
            assert params is not None
            self.tables["processing_jobs"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into eval_runs"):
            assert params is not None
            self.tables["eval_runs"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into eval_datasets"):
            assert params is not None
            self.tables["eval_datasets"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into eval_items"):
            assert params is not None
            self.tables["eval_items"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into agent_runs"):
            assert params is not None
            self.tables["agent_runs"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into agent_steps"):
            assert params is not None
            self.tables["agent_steps"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into agent_tool_calls"):
            assert params is not None
            self.tables["agent_tool_calls"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if "from documents" in normalized and "where document_id" in normalized:
            assert params is not None
            document = self.tables["documents"].get(str(params[0]))
            return FakeCursor([] if document is None else [(document,)])

        if "from documents" in normalized:
            return FakeCursor([(payload,) for payload in self.tables["documents"].values()])

        if "from agent_runs" in normalized:
            return FakeCursor([(payload,) for payload in self.tables["agent_runs"].values()])

        if "from eval_runs" in normalized:
            return FakeCursor([(payload,) for payload in self.tables["eval_runs"].values()])

        if "from eval_datasets" in normalized:
            return FakeCursor([(payload,) for payload in self.tables["eval_datasets"].values()])

        if normalized.startswith("delete from eval_items") and "and item_id" in normalized:
            assert params is not None
            dataset_id = str(params[0])
            item_id = str(params[1])
            self.tables["eval_items"] = {
                key: payload
                for key, payload in self.tables["eval_items"].items()
                if payload["dataset_id"] != dataset_id or payload["item_id"] != item_id
            }
            return FakeCursor([])

        if normalized.startswith("delete from eval_items"):
            assert params is not None
            dataset_id = str(params[0])
            self.tables["eval_items"] = {
                key: payload
                for key, payload in self.tables["eval_items"].items()
                if payload["dataset_id"] != dataset_id
            }
            return FakeCursor([])

        if normalized.startswith("delete from eval_datasets"):
            assert params is not None
            self.tables["eval_datasets"].pop(str(params[0]), None)
            return FakeCursor([])

        if "from eval_items" in normalized and "where dataset_id" in normalized:
            assert params is not None
            return FakeCursor(
                [
                    (payload,)
                    for payload in self.tables["eval_items"].values()
                    if payload["dataset_id"] == str(params[0])
                ]
            )

        if "from eval_items" in normalized:
            return FakeCursor([(payload,) for payload in self.tables["eval_items"].values()])

        raise AssertionError(f"Unhandled SQL statement: {sql}")


def test_local_json_repository_preserves_fallback_metadata_files(tmp_path: Path) -> None:
    repository = LocalJsonDocumentRepository(tmp_path / "data")
    document = _sample_document()

    repository.write_documents([document])

    metadata_path = tmp_path / "data" / "documents.json"
    assert metadata_path.is_file()
    assert repository.list_documents()[0].document_id == "doc-001"
    assert repository.list_documents()[0].chunks[0].source_type == "text_upload"


def test_local_json_repository_manages_eval_datasets_and_items(tmp_path: Path) -> None:
    repository = LocalJsonDocumentRepository(tmp_path / "data")
    dataset = _sample_eval_dataset()
    item = _sample_eval_item(dataset.dataset_id)

    repository.save_eval_dataset(dataset)
    repository.save_eval_item(item)

    assert repository.list_eval_datasets()[0].dataset_id == "eval-dataset-001"
    assert repository.list_eval_items(dataset.dataset_id)[0].query == "付款期限是什麼？"

    updated_item = item.model_copy(update={"query": "更新後的付款期限問題"})
    repository.save_eval_item(updated_item)

    assert repository.list_eval_items(dataset.dataset_id)[0].query == "更新後的付款期限問題"

    repository.delete_eval_item(dataset.dataset_id, item.item_id)

    assert repository.list_eval_items(dataset.dataset_id) == []

    repository.save_eval_item(item)
    repository.delete_eval_dataset(dataset.dataset_id)

    assert repository.list_eval_datasets() == []
    assert repository.list_eval_items(dataset.dataset_id) == []


def test_repository_factory_selects_local_json_and_postgresql(tmp_path: Path) -> None:
    local_settings = Settings(data_dir=tmp_path / "data", repository_provider="local_json")
    postgres_settings = Settings(
        data_dir=tmp_path / "data",
        repository_provider="postgresql",
        database_url="postgresql://docurag:docurag@localhost:5432/docurag",
    )

    local_repository = create_document_repository(local_settings)
    postgres_repository = create_document_repository(postgres_settings)
    storage = create_document_storage(local_settings)

    assert isinstance(local_repository, LocalJsonDocumentRepository)
    assert isinstance(postgres_repository, PostgresDocumentRepository)
    assert storage.repository.name == "local_json"


def test_repository_factory_requires_database_url(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path / "data",
        repository_provider="postgresql",
        database_url=None,
    )

    with pytest.raises(ValueError, match="DOCURAG_DATABASE_URL"):
        create_document_repository(settings)


def test_postgres_repository_supports_core_metadata_round_trip() -> None:
    connection = FakePostgresConnection()
    repository = PostgresDocumentRepository(
        "postgresql://docurag:docurag@localhost:5432/docurag",
        connection_factory=lambda: connection,
    )
    document = _sample_document()
    agent_run = _sample_agent_run()

    repository.write_documents([document])
    repository.write_agent_runs([agent_run])
    repository.save_eval_dataset(_sample_eval_dataset())
    repository.save_eval_item(_sample_eval_item("eval-dataset-001"))
    repository.save_eval_run(
        {
            "run_id": "eval-run-001",
            "created_at": "2026-06-01T00:00:00Z",
            "strategy": "hybrid_rerank",
            "summary": {"case_count": 1},
        }
    )

    assert repository.get_document("doc-001").parser_result.fields.invoice_number.value == "INV-001"
    assert repository.list_documents()[0].chunks[0].chunk_id == "doc-001-chunk-001"
    assert repository.list_agent_runs()[0].run_id == "agent-run-001"
    assert repository.list_eval_datasets()[0].dataset_id == "eval-dataset-001"
    assert repository.list_eval_items("eval-dataset-001")[0].item_id == "eval-item-001"
    assert repository.list_eval_runs()[0]["run_id"] == "eval-run-001"
    assert connection.tables["document_chunks"]["doc-001-chunk-001"]["source_type"] == "text_upload"
    assert connection.tables["extracted_fields"]["doc-001:document_fields"]["fields"]["invoice_number"]["value"] == "INV-001"
    assert connection.tables["agent_steps"]["agent-run-001:step:1"]["tool_name"] == "get_document_fields"
    assert not any("drop table" in statement or "delete from" in statement for statement in connection.statements)


def test_postgres_schema_statements_are_non_destructive() -> None:
    combined_sql = "\n".join(POSTGRES_SCHEMA_STATEMENTS).casefold()

    assert "drop table" not in combined_sql
    assert "delete from" not in combined_sql
    assert "create table if not exists documents" in combined_sql
    assert "create table if not exists agent_runs" in combined_sql
    assert "create table if not exists eval_datasets" in combined_sql
    assert "create table if not exists eval_items" in combined_sql
    assert "create table if not exists eval_runs" in combined_sql


def test_local_json_to_postgresql_migration_command_dry_run(tmp_path: Path) -> None:
    repository = LocalJsonDocumentRepository(tmp_path / "data")
    repository.write_documents([_sample_document()])
    repository.write_agent_runs([_sample_agent_run()])
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "migrate-local-json-to-postgresql.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--data-dir",
            str(tmp_path / "data"),
            "--dry-run",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "documents=1" in result.stdout
    assert "chunks=1" in result.stdout
    assert "parser_results=1" in result.stdout
    assert "agent_runs=1" in result.stdout


def _sample_document() -> DocumentMetadata:
    created_at = datetime(2026, 6, 1, tzinfo=UTC)
    return DocumentMetadata(
        document_id="doc-001",
        project_id=None,
        filename="invoice.txt",
        stored_filename="doc-001-invoice.txt",
        file_type="txt",
        content_type="text/plain",
        size=32,
        status=DocumentStatus.READY,
        created_at=created_at,
        chunks=[
            DocumentChunk(
                chunk_id="doc-001-chunk-001",
                document_id="doc-001",
                text="Invoice number: INV-001",
                source="text_upload",
                created_at=created_at,
                source_type="text_upload",
                metadata={"origin": "uploaded_text"},
            )
        ],
        parser_result=ParserResult(
            document_id="doc-001",
            status=ParserStatus.PARSED,
            fields=DocumentFields(
                invoice_number=ExtractedField(
                    value="INV-001",
                    source_text="Invoice number: INV-001",
                )
            ),
            updated_at=created_at,
        ),
        processing_jobs=[
            ProcessingJob(
                job_id="job-001",
                document_id="doc-001",
                job_type=ProcessingJobType.TEXT_INGESTION,
                status=ProcessingStepStatus.COMPLETED,
                created_at=created_at,
                updated_at=created_at,
            )
        ],
    )


def _sample_eval_dataset() -> EvalDataset:
    created_at = datetime(2026, 6, 1, tzinfo=UTC)
    return EvalDataset(
        dataset_id="eval-dataset-001",
        project_id=None,
        name="Invoice retrieval dataset",
        description="Demo-safe eval dataset",
        created_at=created_at,
        updated_at=created_at,
    )


def _sample_eval_item(dataset_id: str) -> EvalItem:
    created_at = datetime(2026, 6, 1, tzinfo=UTC)
    return EvalItem(
        item_id="eval-item-001",
        dataset_id=dataset_id,
        project_id=None,
        query="付款期限是什麼？",
        expected_terms=["Net 15"],
        expected_document_ids=["doc-001"],
        expected_chunk_ids=["doc-001-chunk-001"],
        tags=["invoice"],
        notes="demo-safe item",
        created_at=created_at,
        updated_at=created_at,
    )


def _sample_agent_run() -> AgentRun:
    return AgentRun(
        run_id="agent-run-001",
        status=AgentRunStatus.COMPLETED,
        task="summarize invoice fields",
        document_id="doc-001",
        query="invoice number",
        plan_steps=[
            AgentStep(
                step_id="step-001",
                order=1,
                title="Read fields",
                tool_name="get_document_fields",
                status=AgentRunStatus.COMPLETED,
            )
        ],
        final_answer=AgentFinalAnswer(
            text="Invoice INV-001",
            status=AgentRunStatus.COMPLETED,
        ),
        created_at="2026-06-01T00:00:00Z",
        updated_at="2026-06-01T00:00:01Z",
    )


def _payload(value: object) -> dict[str, Any]:
    payload = getattr(value, "obj", value)
    assert isinstance(payload, dict)
    return payload
