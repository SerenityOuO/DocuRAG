from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from app.schemas.agent import AgentRun
from app.schemas.documents import DocumentMetadata
from app.schemas.evaluation import EvalDataset, EvalItem


class DocumentMetadataRepository(Protocol):
    name: str

    def list_documents(self) -> list[DocumentMetadata]:
        ...

    def write_documents(self, documents: list[DocumentMetadata]) -> None:
        ...

    def list_agent_runs(self) -> list[AgentRun]:
        ...

    def write_agent_runs(self, agent_runs: list[AgentRun]) -> None:
        ...

    def list_eval_datasets(self) -> list[EvalDataset]:
        ...

    def save_eval_dataset(self, dataset: EvalDataset) -> None:
        ...

    def delete_eval_dataset(self, dataset_id: str) -> None:
        ...

    def list_eval_items(self, dataset_id: str | None = None) -> list[EvalItem]:
        ...

    def save_eval_item(self, item: EvalItem) -> None:
        ...

    def delete_eval_item(self, dataset_id: str, item_id: str) -> None:
        ...


class LocalJsonDocumentRepository:
    name = "local_json"

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.metadata_path = data_dir / "documents.json"
        self.agent_runs_path = data_dir / "agent_runs.json"
        self.eval_datasets_path = data_dir / "eval_datasets.json"
        self.eval_items_path = data_dir / "eval_items.json"

    def list_documents(self) -> list[DocumentMetadata]:
        self._ensure_documents_storage()
        raw_documents = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        return [DocumentMetadata.model_validate(raw_document) for raw_document in raw_documents]

    def write_documents(self, documents: list[DocumentMetadata]) -> None:
        self._write_json(
            self.metadata_path,
            [document.model_dump(mode="json") for document in documents],
        )

    def list_agent_runs(self) -> list[AgentRun]:
        self._ensure_agent_run_storage()
        raw_agent_runs = json.loads(self.agent_runs_path.read_text(encoding="utf-8"))
        return [AgentRun.model_validate(raw_agent_run) for raw_agent_run in raw_agent_runs]

    def write_agent_runs(self, agent_runs: list[AgentRun]) -> None:
        self._write_json(
            self.agent_runs_path,
            [agent_run.model_dump(mode="json") for agent_run in agent_runs],
        )

    def list_eval_datasets(self) -> list[EvalDataset]:
        raw_datasets = self._read_json_list(self.eval_datasets_path)
        return [EvalDataset.model_validate(raw_dataset) for raw_dataset in raw_datasets]

    def save_eval_dataset(self, dataset: EvalDataset) -> None:
        datasets = self.list_eval_datasets()
        for index, saved_dataset in enumerate(datasets):
            if saved_dataset.dataset_id == dataset.dataset_id:
                datasets[index] = dataset
                self._write_json(
                    self.eval_datasets_path,
                    [saved.model_dump(mode="json") for saved in datasets],
                )
                return

        datasets.append(dataset)
        self._write_json(
            self.eval_datasets_path,
            [saved.model_dump(mode="json") for saved in datasets],
        )

    def delete_eval_dataset(self, dataset_id: str) -> None:
        datasets = [
            dataset
            for dataset in self.list_eval_datasets()
            if dataset.dataset_id != dataset_id
        ]
        items = [
            item
            for item in self.list_eval_items()
            if item.dataset_id != dataset_id
        ]
        self._write_json(
            self.eval_datasets_path,
            [dataset.model_dump(mode="json") for dataset in datasets],
        )
        self._write_json(
            self.eval_items_path,
            [item.model_dump(mode="json") for item in items],
        )

    def list_eval_items(self, dataset_id: str | None = None) -> list[EvalItem]:
        raw_items = self._read_json_list(self.eval_items_path)
        items = [EvalItem.model_validate(raw_item) for raw_item in raw_items]
        if dataset_id is None:
            return items

        return [item for item in items if item.dataset_id == dataset_id]

    def save_eval_item(self, item: EvalItem) -> None:
        items = self.list_eval_items()
        for index, saved_item in enumerate(items):
            if saved_item.item_id == item.item_id and saved_item.dataset_id == item.dataset_id:
                items[index] = item
                self._write_json(
                    self.eval_items_path,
                    [saved.model_dump(mode="json") for saved in items],
                )
                return

        items.append(item)
        self._write_json(
            self.eval_items_path,
            [saved.model_dump(mode="json") for saved in items],
        )

    def delete_eval_item(self, dataset_id: str, item_id: str) -> None:
        items = [
            item
            for item in self.list_eval_items()
            if item.dataset_id != dataset_id or item.item_id != item_id
        ]
        self._write_json(
            self.eval_items_path,
            [item.model_dump(mode="json") for item in items],
        )

    def _ensure_documents_storage(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.metadata_path.exists():
            self.metadata_path.write_text("[]\n", encoding="utf-8")

    def _ensure_agent_run_storage(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.agent_runs_path.exists():
            self.agent_runs_path.write_text("[]\n", encoding="utf-8")

    def _read_json_list(self, path: Path) -> list[dict[str, Any]]:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("[]\n", encoding="utf-8")

        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"Expected list payload in {path.name}.")

        return [dict(item) for item in payload if isinstance(item, dict)]

    def _write_json(self, path: Path, payload: list[dict[str, Any]]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        temp_path = path.with_name(f"{path.name}.{uuid4().hex}.tmp")
        temp_path.write_text(content, encoding="utf-8")

        try:
            temp_path.replace(path)
        except OSError:
            # Docker Desktop bind mounts on Windows can reject atomic replace.
            path.write_text(content, encoding="utf-8")
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


POSTGRES_SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS documents (
        document_id TEXT PRIMARY KEY,
        project_id TEXT NULL,
        filename TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NULL,
        payload JSONB NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents (project_id)",
    "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents (status)",
    """
    CREATE TABLE IF NOT EXISTS document_pages (
        page_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        project_id TEXT NULL,
        page_number INTEGER NOT NULL,
        payload JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS document_chunks (
        chunk_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        project_id TEXT NULL,
        source_type TEXT NOT NULL,
        page_number INTEGER NULL,
        created_at TIMESTAMPTZ NOT NULL,
        payload JSONB NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks (document_id)",
    "CREATE INDEX IF NOT EXISTS idx_document_chunks_project_id ON document_chunks (project_id)",
    """
    CREATE TABLE IF NOT EXISTS extracted_fields (
        field_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        project_id TEXT NULL,
        field_name TEXT NOT NULL,
        updated_at TIMESTAMPTZ NULL,
        payload JSONB NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_extracted_fields_document_id ON extracted_fields (document_id)",
    """
    CREATE TABLE IF NOT EXISTS processing_jobs (
        job_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        project_id TEXT NULL,
        job_type TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL,
        payload JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS eval_datasets (
        dataset_id TEXT PRIMARY KEY,
        project_id TEXT NULL,
        name TEXT NOT NULL,
        payload JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS eval_items (
        item_id TEXT PRIMARY KEY,
        dataset_id TEXT NOT NULL,
        project_id TEXT NULL,
        payload JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS eval_runs (
        run_id TEXT PRIMARY KEY,
        project_id TEXT NULL,
        strategy TEXT NULL,
        created_at TIMESTAMPTZ NULL,
        payload JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS eval_run_items (
        run_item_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        project_id TEXT NULL,
        payload JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_runs (
        run_id TEXT PRIMARY KEY,
        document_id TEXT NULL,
        project_id TEXT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        payload JSONB NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_agent_runs_document_id ON agent_runs (document_id)",
    """
    CREATE TABLE IF NOT EXISTS agent_steps (
        step_row_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        step_id TEXT NOT NULL,
        step_order INTEGER NOT NULL,
        payload JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_tool_calls (
        tool_call_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        tool_name TEXT NOT NULL,
        call_order INTEGER NOT NULL,
        payload JSONB NOT NULL
    )
    """,
]


class PostgresDocumentRepository:
    name = "postgresql"

    def __init__(
        self,
        database_url: str,
        connection_factory: Callable[[], Any] | None = None,
    ) -> None:
        if not database_url:
            raise ValueError("PostgreSQL repository requires DOCURAG_DATABASE_URL.")

        self.database_url = database_url
        self._connection_factory = connection_factory

    def ensure_schema(self) -> None:
        with self._connect() as connection:
            for statement in POSTGRES_SCHEMA_STATEMENTS:
                connection.execute(statement)

    def list_documents(self) -> list[DocumentMetadata]:
        self.ensure_schema()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM documents
                ORDER BY created_at DESC, document_id ASC
                """
            ).fetchall()

        return [DocumentMetadata.model_validate(_row_payload(row)) for row in rows]

    def write_documents(self, documents: list[DocumentMetadata]) -> None:
        self.ensure_schema()
        with self._connect() as connection:
            for document in documents:
                payload = document.model_dump(mode="json")
                updated_at = _document_updated_at(document)
                connection.execute(
                    """
                    INSERT INTO documents (
                        document_id, project_id, filename, status, created_at, updated_at, payload
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (document_id) DO UPDATE SET
                        project_id = EXCLUDED.project_id,
                        filename = EXCLUDED.filename,
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at,
                        payload = EXCLUDED.payload
                    """,
                    (
                        document.document_id,
                        document.project_id,
                        document.filename,
                        str(document.status),
                        document.created_at,
                        updated_at,
                        _json_payload(payload),
                    ),
                )
                self._upsert_document_children(connection, document)

    def get_document(self, document_id: str) -> DocumentMetadata | None:
        self.ensure_schema()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM documents WHERE document_id = %s",
                (document_id,),
            ).fetchall()

        if not rows:
            return None

        return DocumentMetadata.model_validate(_row_payload(rows[0]))

    def list_agent_runs(self) -> list[AgentRun]:
        self.ensure_schema()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM agent_runs
                ORDER BY created_at DESC, run_id ASC
                """
            ).fetchall()

        return [AgentRun.model_validate(_row_payload(row)) for row in rows]

    def write_agent_runs(self, agent_runs: list[AgentRun]) -> None:
        self.ensure_schema()
        with self._connect() as connection:
            for agent_run in agent_runs:
                payload = agent_run.model_dump(mode="json")
                connection.execute(
                    """
                    INSERT INTO agent_runs (
                        run_id, document_id, project_id, status, created_at, updated_at, payload
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO UPDATE SET
                        document_id = EXCLUDED.document_id,
                        project_id = EXCLUDED.project_id,
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at,
                        payload = EXCLUDED.payload
                    """,
                    (
                        agent_run.run_id,
                        agent_run.document_id,
                        None,
                        str(agent_run.status),
                        agent_run.created_at,
                        agent_run.updated_at,
                        _json_payload(payload),
                    ),
                )
                for step_index, step in enumerate(agent_run.plan_steps, start=1):
                    connection.execute(
                        """
                        INSERT INTO agent_steps (step_row_id, run_id, step_id, step_order, payload)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (step_row_id) DO UPDATE SET
                            step_order = EXCLUDED.step_order,
                            payload = EXCLUDED.payload
                        """,
                        (
                            f"{agent_run.run_id}:step:{step_index}",
                            agent_run.run_id,
                            step.step_id,
                            step_index,
                            _json_payload(step.model_dump(mode="json")),
                        ),
                    )
                for call_index, tool_call in enumerate(agent_run.tool_calls, start=1):
                    connection.execute(
                        """
                        INSERT INTO agent_tool_calls (tool_call_id, run_id, tool_name, call_order, payload)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (tool_call_id) DO UPDATE SET
                            tool_name = EXCLUDED.tool_name,
                            call_order = EXCLUDED.call_order,
                            payload = EXCLUDED.payload
                        """,
                        (
                            f"{agent_run.run_id}:tool:{call_index}",
                            agent_run.run_id,
                            str(tool_call.tool_name),
                            call_index,
                            _json_payload(tool_call.model_dump(mode="json")),
                        ),
                    )

    def save_eval_run(self, eval_run: dict[str, Any]) -> None:
        self.ensure_schema()
        run_id = str(eval_run.get("run_id") or "")
        if not run_id:
            raise ValueError("Eval run payload requires run_id.")

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO eval_runs (run_id, project_id, strategy, created_at, payload)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (run_id) DO UPDATE SET
                    project_id = EXCLUDED.project_id,
                    strategy = EXCLUDED.strategy,
                    created_at = EXCLUDED.created_at,
                    payload = EXCLUDED.payload
                """,
                (
                    run_id,
                    eval_run.get("project_id"),
                    eval_run.get("strategy"),
                    _parse_optional_datetime(eval_run.get("created_at")),
                    _json_payload(eval_run),
                ),
            )

    def list_eval_runs(self) -> list[dict[str, Any]]:
        self.ensure_schema()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM eval_runs
                ORDER BY created_at DESC NULLS LAST, run_id ASC
                """
            ).fetchall()

        return [dict(_row_payload(row)) for row in rows]

    def list_eval_datasets(self) -> list[EvalDataset]:
        self.ensure_schema()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM eval_datasets
                ORDER BY name ASC, dataset_id ASC
                """
            ).fetchall()

        return [EvalDataset.model_validate(_row_payload(row)) for row in rows]

    def save_eval_dataset(self, dataset: EvalDataset) -> None:
        self.ensure_schema()
        payload = dataset.model_dump(mode="json")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO eval_datasets (dataset_id, project_id, name, payload)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (dataset_id) DO UPDATE SET
                    project_id = EXCLUDED.project_id,
                    name = EXCLUDED.name,
                    payload = EXCLUDED.payload
                """,
                (
                    dataset.dataset_id,
                    dataset.project_id,
                    dataset.name,
                    _json_payload(payload),
                ),
            )

    def delete_eval_dataset(self, dataset_id: str) -> None:
        self.ensure_schema()
        with self._connect() as connection:
            connection.execute("DELETE FROM eval_items WHERE dataset_id = %s", (dataset_id,))
            connection.execute("DELETE FROM eval_datasets WHERE dataset_id = %s", (dataset_id,))

    def list_eval_items(self, dataset_id: str | None = None) -> list[EvalItem]:
        self.ensure_schema()
        with self._connect() as connection:
            if dataset_id is None:
                rows = connection.execute(
                    """
                    SELECT payload
                    FROM eval_items
                    ORDER BY item_id ASC
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT payload
                    FROM eval_items
                    WHERE dataset_id = %s
                    ORDER BY item_id ASC
                    """,
                    (dataset_id,),
                ).fetchall()

        return [EvalItem.model_validate(_row_payload(row)) for row in rows]

    def save_eval_item(self, item: EvalItem) -> None:
        self.ensure_schema()
        payload = item.model_dump(mode="json")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO eval_items (item_id, dataset_id, project_id, payload)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (item_id) DO UPDATE SET
                    dataset_id = EXCLUDED.dataset_id,
                    project_id = EXCLUDED.project_id,
                    payload = EXCLUDED.payload
                """,
                (
                    item.item_id,
                    item.dataset_id,
                    item.project_id,
                    _json_payload(payload),
                ),
            )

    def delete_eval_item(self, dataset_id: str, item_id: str) -> None:
        self.ensure_schema()
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM eval_items WHERE dataset_id = %s AND item_id = %s",
                (dataset_id, item_id),
            )

    def _upsert_document_children(self, connection: Any, document: DocumentMetadata) -> None:
        for chunk in document.chunks:
            connection.execute(
                """
                INSERT INTO document_chunks (
                    chunk_id, document_id, project_id, source_type, page_number, created_at, payload
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    project_id = EXCLUDED.project_id,
                    source_type = EXCLUDED.source_type,
                    page_number = EXCLUDED.page_number,
                    payload = EXCLUDED.payload
                """,
                (
                    chunk.chunk_id,
                    document.document_id,
                    document.project_id,
                    chunk.source_type,
                    chunk.page_number,
                    chunk.created_at,
                    _json_payload(chunk.model_dump(mode="json")),
                ),
            )

        if document.parser_result is not None:
            connection.execute(
                """
                INSERT INTO extracted_fields (
                    field_id, document_id, project_id, field_name, updated_at, payload
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (field_id) DO UPDATE SET
                    project_id = EXCLUDED.project_id,
                    updated_at = EXCLUDED.updated_at,
                    payload = EXCLUDED.payload
                """,
                (
                    f"{document.document_id}:document_fields",
                    document.document_id,
                    document.project_id,
                    "document_fields",
                    document.parser_result.updated_at,
                    _json_payload(document.parser_result.model_dump(mode="json")),
                ),
            )

        for job in document.processing_jobs:
            connection.execute(
                """
                INSERT INTO processing_jobs (
                    job_id, document_id, project_id, job_type, status, created_at, updated_at, payload
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO UPDATE SET
                    project_id = EXCLUDED.project_id,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at,
                    payload = EXCLUDED.payload
                """,
                (
                    job.job_id,
                    document.document_id,
                    document.project_id,
                    str(job.job_type),
                    str(job.status),
                    job.created_at,
                    job.updated_at,
                    _json_payload(job.model_dump(mode="json")),
                ),
            )

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()

        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL repository requires the optional postgres dependency. "
                'Install the backend with ".[postgres]" before enabling '
                "DOCURAG_REPOSITORY_PROVIDER=postgresql."
            ) from exc

        return psycopg.connect(self.database_url)


def create_document_repository(settings: Any) -> DocumentMetadataRepository:
    provider = str(getattr(settings, "repository_provider", "local_json")).strip().lower()

    if provider in {"local", "local_json", "json"}:
        return LocalJsonDocumentRepository(settings.data_dir)

    if provider in {"postgresql", "postgres", "db"}:
        database_url = getattr(settings, "database_url", None)
        if not database_url:
            raise ValueError("DOCURAG_DATABASE_URL is required when DOCURAG_REPOSITORY_PROVIDER=postgresql.")

        return PostgresDocumentRepository(str(database_url))

    raise ValueError(f"Unsupported repository provider configured: {provider}")


def create_document_storage(settings: Any):
    from app.services.document_storage import DocumentStorage

    return DocumentStorage(
        settings.data_dir,
        repository=create_document_repository(settings),
        pdf_render_dpi=settings.pdf_render_dpi,
        pdf_render_max_side=settings.pdf_render_max_side,
    )


def _json_payload(payload: dict[str, Any]) -> Any:
    try:
        from psycopg.types.json import Jsonb
    except ImportError:
        return payload

    return Jsonb(payload)


def _row_payload(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        payload = row.get("payload", row)
    else:
        payload = row[0]

    return getattr(payload, "obj", payload)


def _document_updated_at(document: DocumentMetadata) -> datetime | None:
    if document.processing.updated_at is not None:
        return document.processing.updated_at

    if document.parser_result is not None and document.parser_result.updated_at is not None:
        return document.parser_result.updated_at

    if document.ocr.updated_at is not None:
        return document.ocr.updated_at

    return document.created_at


def _parse_optional_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value

    if not isinstance(value, str) or not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
