from datetime import UTC, datetime
import json
from pathlib import Path
import re
from uuid import uuid4

from fastapi import UploadFile

from app.schemas.agent import AgentRun
from app.schemas.documents import (
    DocumentChunk,
    DocumentMetadata,
    DocumentStatus,
    OcrResult,
    OcrStatus,
    OcrTextLine,
    ParserResult,
    ParserStatus,
    ProcessingJob,
    ProcessingJobType,
    ProcessingStatus,
    ProcessingStepStatus,
)
from app.services.ocr import OcrProvider


class DocumentStorage:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.upload_dir = data_dir / "uploads"
        self.metadata_path = data_dir / "documents.json"
        self.agent_runs_path = data_dir / "agent_runs.json"

    def list_documents(self) -> list[DocumentMetadata]:
        documents = self._read_documents()
        return sorted(documents, key=lambda document: document.created_at, reverse=True)

    def get_document(self, document_id: str) -> DocumentMetadata | None:
        for document in self._read_documents():
            if document.document_id == document_id:
                return document

        return None

    def get_ocr_result(self, document_id: str) -> OcrResult | None:
        document = self.get_document(document_id)

        if document is None:
            return None

        return document.ocr or OcrResult(status=OcrStatus.PENDING)

    def get_parser_result(self, document_id: str) -> ParserResult | None:
        document = self.get_document(document_id)

        if document is None:
            return None

        if document.parser_result is not None:
            return document.parser_result

        return ParserResult(
            document_id=document.document_id,
            status=ParserStatus.PENDING,
            source_ocr_status=document.ocr.status,
            source_ocr_updated_at=document.ocr.updated_at,
            trace_metadata={
                "input": "ocr_lines" if document.ocr.lines else "ocr_text",
                "parser_mode": "deterministic",
            },
        )

    def get_agent_run(self, run_id: str) -> AgentRun | None:
        for agent_run in self._read_agent_runs():
            if agent_run.run_id == run_id:
                return agent_run

        return None

    def save_agent_run(self, agent_run: AgentRun) -> AgentRun:
        agent_runs = self._read_agent_runs()

        for index, saved_agent_run in enumerate(agent_runs):
            if saved_agent_run.run_id == agent_run.run_id:
                agent_runs[index] = agent_run
                self._write_agent_runs(agent_runs)
                return agent_run

        agent_runs.append(agent_run)
        self._write_agent_runs(agent_runs)

        return agent_run

    def list_documents_for_rag(self) -> list[DocumentMetadata]:
        documents = self._read_documents()
        documents_changed = False

        for index, document in enumerate(documents):
            if (
                not document.chunks
                and document.ocr.status == OcrStatus.COMPLETED
                and document.ocr.text.strip()
            ):
                document.chunks = self._build_chunks(
                    document.document_id,
                    document.ocr.text,
                    document.ocr.updated_at or datetime.now(UTC),
                    source=document.ocr.extracted_fields.get("chunk_source", "ocr_mock"),
                    ocr_lines=document.ocr.lines,
                )
                document.status = DocumentStatus.READY
                document.processing = ProcessingStatus(
                    upload=ProcessingStepStatus.COMPLETED,
                    ocr=ProcessingStepStatus.COMPLETED,
                    indexing=ProcessingStepStatus.COMPLETED,
                    ready=True,
                    updated_at=document.ocr.updated_at or datetime.now(UTC),
                )
                self._record_job(
                    document,
                    ProcessingJobType.LOCAL_INDEXING,
                    ProcessingStepStatus.COMPLETED,
                    document.ocr.updated_at or datetime.now(UTC),
                )
                documents[index] = document
                documents_changed = True

        if documents_changed:
            self._write_documents(documents)

        return documents

    def get_file_path(self, document: DocumentMetadata) -> Path | None:
        upload_root = self.upload_dir.resolve()
        file_path = (upload_root / document.stored_filename).resolve()

        try:
            file_path.relative_to(upload_root)
        except ValueError:
            return None

        if not file_path.is_file():
            return None

        return file_path

    async def save_upload(self, file: UploadFile) -> DocumentMetadata:
        self._ensure_storage()

        content = await file.read()
        filename = self._safe_filename(file.filename or "uploaded-file")
        document_id = str(uuid4())
        stored_filename = f"{document_id}-{filename}"
        upload_root = self.upload_dir.resolve()
        upload_path = (upload_root / stored_filename).resolve()
        upload_path.relative_to(upload_root)
        upload_path.write_bytes(content)

        created_at = datetime.now(UTC)
        document = DocumentMetadata(
            document_id=document_id,
            project_id=None,
            filename=filename,
            stored_filename=stored_filename,
            file_type=Path(filename).suffix.lstrip(".").lower() or "unknown",
            content_type=file.content_type or "application/octet-stream",
            size=len(content),
            status=DocumentStatus.UPLOADED,
            created_at=created_at,
            processing=ProcessingStatus(updated_at=created_at),
        )
        self._record_job(
            document,
            ProcessingJobType.UPLOAD,
            ProcessingStepStatus.COMPLETED,
            created_at,
        )

        documents = self._read_documents()
        documents.append(document)
        self._write_documents(documents)

        return document

    def run_ocr(self, document_id: str, provider: OcrProvider) -> OcrResult | None:
        documents = self._read_documents()

        for index, document in enumerate(documents):
            if document.document_id != document_id:
                continue

            now = datetime.now(UTC)
            ocr_result = provider.extract(document, self.get_file_path(document), now)
            document.ocr = ocr_result
            ocr_job_type = provider.job_type

            if ocr_result.status == OcrStatus.COMPLETED:
                document.chunks = self._build_chunks(
                    document.document_id,
                    ocr_result.text,
                    now,
                    source=provider.chunk_source,
                    ocr_lines=ocr_result.lines,
                )
                document.status = DocumentStatus.READY
                document.processing = ProcessingStatus(
                    upload=ProcessingStepStatus.COMPLETED,
                    ocr=ProcessingStepStatus.COMPLETED,
                    indexing=ProcessingStepStatus.COMPLETED,
                    ready=True,
                    updated_at=now,
                )
                self._record_job(
                    document,
                    ocr_job_type,
                    ProcessingStepStatus.COMPLETED,
                    now,
                )
                self._record_job(
                    document,
                    ProcessingJobType.LOCAL_INDEXING,
                    ProcessingStepStatus.COMPLETED,
                    now,
                )
            elif ocr_result.status == OcrStatus.FAILED:
                document.chunks = []
                document.status = DocumentStatus.FAILED
                document.processing = ProcessingStatus(
                    upload=ProcessingStepStatus.COMPLETED,
                    ocr=ProcessingStepStatus.FAILED,
                    indexing=ProcessingStepStatus.PENDING,
                    ready=False,
                    failed_reason=ocr_result.extracted_fields.get("error", "OCR failed"),
                    updated_at=now,
                )
                self._record_job(
                    document,
                    ocr_job_type,
                    ProcessingStepStatus.FAILED,
                    now,
                    error_message=ocr_result.extracted_fields.get("error", "OCR failed"),
                )
            else:
                document.chunks = []
                document.status = DocumentStatus.PROCESSING
                ocr_step_status = (
                    ProcessingStepStatus.RUNNING
                    if ocr_result.status == OcrStatus.RUNNING
                    else ProcessingStepStatus.PENDING
                )
                document.processing = ProcessingStatus(
                    upload=ProcessingStepStatus.COMPLETED,
                    ocr=ocr_step_status,
                    indexing=ProcessingStepStatus.PENDING,
                    ready=False,
                    updated_at=now,
                )
                self._record_job(
                    document,
                    ocr_job_type,
                    ocr_step_status,
                    now,
                )

            documents[index] = document
            self._write_documents(documents)

            return ocr_result

        return None

    def run_parser(
        self,
        document_id: str,
        parser,
    ) -> ParserResult | None:
        documents = self._read_documents()

        for index, document in enumerate(documents):
            if document.document_id != document_id:
                continue

            now = datetime.now(UTC)
            parser_result = parser.parse(document, parsed_at=now)
            document.parser_result = parser_result
            document.processing.parser = (
                ProcessingStepStatus.COMPLETED
                if parser_result.status == ParserStatus.PARSED
                else ProcessingStepStatus.FAILED
            )
            document.processing.updated_at = now
            self._record_job(
                document,
                ProcessingJobType.PARSER,
                document.processing.parser,
                now,
                error_message=parser_result.error_message or parser_result.fallback_reason,
            )

            documents[index] = document
            self._write_documents(documents)

            return parser_result

        return None

    def _ensure_storage(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        if not self.metadata_path.exists():
            self.metadata_path.write_text("[]\n", encoding="utf-8")

    def _read_documents(self) -> list[DocumentMetadata]:
        self._ensure_storage()

        raw_documents = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        return [DocumentMetadata.model_validate(raw_document) for raw_document in raw_documents]

    def _ensure_agent_run_storage(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.agent_runs_path.exists():
            self.agent_runs_path.write_text("[]\n", encoding="utf-8")

    def _read_agent_runs(self) -> list[AgentRun]:
        self._ensure_agent_run_storage()

        raw_agent_runs = json.loads(self.agent_runs_path.read_text(encoding="utf-8"))
        return [AgentRun.model_validate(raw_agent_run) for raw_agent_run in raw_agent_runs]

    def _write_agent_runs(self, agent_runs: list[AgentRun]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        payload = [agent_run.model_dump(mode="json") for agent_run in agent_runs]
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        temp_path = self.agent_runs_path.with_name(f"{self.agent_runs_path.name}.{uuid4().hex}.tmp")
        temp_path.write_text(content, encoding="utf-8")

        try:
            temp_path.replace(self.agent_runs_path)
        except OSError:
            # Docker Desktop bind mounts on Windows can reject atomic replace.
            self.agent_runs_path.write_text(content, encoding="utf-8")
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    def _write_documents(self, documents: list[DocumentMetadata]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        payload = [document.model_dump(mode="json") for document in documents]
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        temp_path = self.metadata_path.with_name(f"{self.metadata_path.name}.{uuid4().hex}.tmp")
        temp_path.write_text(content, encoding="utf-8")

        try:
            temp_path.replace(self.metadata_path)
        except OSError:
            # Docker Desktop bind mounts on Windows can reject atomic replace.
            self.metadata_path.write_text(content, encoding="utf-8")
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    def _safe_filename(self, filename: str) -> str:
        name = Path(filename.replace("\\", "/")).name
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")

        return name or "uploaded-file"

    def _build_chunks(
        self,
        document_id: str,
        text: str,
        created_at: datetime,
        source: str = "ocr_mock",
        ocr_lines: list[OcrTextLine] | None = None,
    ) -> list[DocumentChunk]:
        if ocr_lines:
            chunks = []

            for line in ocr_lines:
                clean_text = line.text.strip()

                if not clean_text:
                    continue

                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{document_id}-chunk-{len(chunks) + 1:03d}",
                        document_id=document_id,
                        text=clean_text,
                        source=source,
                        created_at=created_at,
                        page_number=line.page_number,
                        bbox=line.bbox,
                        confidence=line.confidence,
                        source_type=source,
                        metadata={
                            **line.metadata,
                            "origin": "ocr_line",
                            "provider": source,
                        },
                    )
                )

            if chunks:
                return chunks

        chunks: list[DocumentChunk] = []
        current_lines: list[str] = []
        current_size = 0
        max_chunk_size = 360

        for line in text.splitlines():
            clean_line = line.strip()

            if not clean_line:
                continue

            separator_size = 1 if current_lines else 0
            next_size = current_size + len(clean_line) + separator_size
            if current_lines and next_size > max_chunk_size:
                chunk_text = "\n".join(current_lines)
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{document_id}-chunk-{len(chunks) + 1:03d}",
                        document_id=document_id,
                        text=chunk_text,
                        source=source,
                        created_at=created_at,
                        source_type=source,
                        metadata={"origin": "ocr_text", "provider": source},
                    )
                )
                current_lines = []
                current_size = 0

            current_lines.append(clean_line)
            current_size += len(clean_line) + separator_size

        if current_lines:
            chunk_text = "\n".join(current_lines)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document_id}-chunk-{len(chunks) + 1:03d}",
                    document_id=document_id,
                    text=chunk_text,
                    source=source,
                    created_at=created_at,
                    source_type=source,
                    metadata={"origin": "ocr_text", "provider": source},
                )
            )

        return chunks

    def _record_job(
        self,
        document: DocumentMetadata,
        job_type: ProcessingJobType,
        status: ProcessingStepStatus,
        timestamp: datetime,
        error_message: str | None = None,
    ) -> None:
        job = ProcessingJob(
            job_id=f"job-{uuid4()}",
            document_id=document.document_id,
            job_type=job_type,
            status=status,
            created_at=timestamp,
            updated_at=timestamp,
            error_message=error_message,
        )
        document.processing_jobs.append(job)
        document.latest_job = job
