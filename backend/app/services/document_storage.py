from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
import re
from uuid import uuid4

from fastapi import UploadFile
from pypdf import PdfReader

from app.repositories.document_metadata import DocumentMetadataRepository, LocalJsonDocumentRepository
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
    PdfPageImage,
    ProcessingJob,
    ProcessingJobType,
    ProcessingStatus,
    ProcessingStepStatus,
)
from app.schemas.evaluation import (
    EvalDataset,
    EvalDatasetCreateRequest,
    EvalDatasetUpdateRequest,
    EvalItem,
    EvalItemCreateRequest,
    EvalItemUpdateRequest,
)
from app.services.ocr import OcrProvider
from app.services.pdf_rendering import PdfPageRenderer, PdfRenderingError


class DocumentStorage:
    def __init__(
        self,
        data_dir: Path,
        repository: DocumentMetadataRepository | None = None,
        pdf_renderer: PdfPageRenderer | None = None,
        pdf_render_dpi: int = 150,
        pdf_render_max_side: int = 1800,
    ) -> None:
        self.data_dir = data_dir
        self.upload_dir = data_dir / "uploads"
        self.metadata_path = data_dir / "documents.json"
        self.agent_runs_path = data_dir / "agent_runs.json"
        self.repository = repository or LocalJsonDocumentRepository(data_dir)
        self.pdf_renderer = pdf_renderer or PdfPageRenderer(
            data_dir,
            dpi=pdf_render_dpi,
            max_side=pdf_render_max_side,
        )

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

    def list_eval_datasets(self, project_ids: frozenset[str] | None = None) -> list[EvalDataset]:
        datasets = [
            dataset
            for dataset in self.repository.list_eval_datasets()
            if self._project_visible(dataset.project_id, project_ids)
        ]
        items = [
            item
            for item in self.repository.list_eval_items()
            if self._project_visible(item.project_id, project_ids)
        ]
        item_counts: dict[str, int] = {}
        for item in items:
            item_counts[item.dataset_id] = item_counts.get(item.dataset_id, 0) + 1

        return sorted(
            [
                dataset.model_copy(update={"item_count": item_counts.get(dataset.dataset_id, 0)})
                for dataset in datasets
            ],
            key=lambda dataset: dataset.updated_at,
            reverse=True,
        )

    def get_eval_dataset(self, dataset_id: str) -> EvalDataset | None:
        for dataset in self.repository.list_eval_datasets():
            if dataset.dataset_id == dataset_id:
                item_count = len(self.repository.list_eval_items(dataset_id))
                return dataset.model_copy(update={"item_count": item_count})

        return None

    def create_eval_dataset(
        self,
        request: EvalDatasetCreateRequest,
        project_id: str | None = None,
    ) -> EvalDataset:
        now = datetime.now(UTC)
        dataset = EvalDataset(
            dataset_id=f"eval-dataset-{uuid4().hex[:12]}",
            project_id=project_id,
            name=self._required_text(request.name, "Eval dataset name"),
            description=self._optional_text(request.description),
            created_at=now,
            updated_at=now,
        )
        self.repository.save_eval_dataset(dataset)
        return dataset

    def update_eval_dataset(
        self,
        dataset_id: str,
        request: EvalDatasetUpdateRequest,
    ) -> EvalDataset | None:
        dataset = self.get_eval_dataset(dataset_id)
        if dataset is None:
            return None

        updates: dict[str, object] = {"updated_at": datetime.now(UTC)}
        if "name" in request.model_fields_set and request.name is not None:
            updates["name"] = self._required_text(request.name, "Eval dataset name")
        if "description" in request.model_fields_set:
            updates["description"] = self._optional_text(request.description)

        updated_dataset = dataset.model_copy(update=updates)
        self.repository.save_eval_dataset(updated_dataset)
        return self.get_eval_dataset(dataset_id)

    def delete_eval_dataset(self, dataset_id: str) -> bool:
        if self.get_eval_dataset(dataset_id) is None:
            return False

        self.repository.delete_eval_dataset(dataset_id)
        return True

    def list_eval_items(self, dataset_id: str) -> list[EvalItem]:
        return sorted(
            self.repository.list_eval_items(dataset_id),
            key=lambda item: item.updated_at,
            reverse=True,
        )

    def get_eval_item(self, dataset_id: str, item_id: str) -> EvalItem | None:
        for item in self.repository.list_eval_items(dataset_id):
            if item.item_id == item_id:
                return item

        return None

    def create_eval_item(
        self,
        dataset: EvalDataset,
        request: EvalItemCreateRequest,
    ) -> EvalItem:
        now = datetime.now(UTC)
        item = EvalItem(
            item_id=f"eval-item-{uuid4().hex[:12]}",
            dataset_id=dataset.dataset_id,
            project_id=dataset.project_id,
            query=self._required_text(request.query, "Eval item query"),
            expected_terms=self._clean_required_list(request.expected_terms, "expected_terms"),
            expected_document_ids=self._clean_optional_list(request.expected_document_ids),
            expected_chunk_ids=self._clean_optional_list(request.expected_chunk_ids),
            tags=self._clean_optional_list(request.tags),
            notes=self._optional_text(request.notes),
            created_at=now,
            updated_at=now,
        )
        self.repository.save_eval_item(item)
        return item

    def update_eval_item(
        self,
        dataset_id: str,
        item_id: str,
        request: EvalItemUpdateRequest,
    ) -> EvalItem | None:
        item = self.get_eval_item(dataset_id, item_id)
        if item is None:
            return None

        updates: dict[str, object] = {"updated_at": datetime.now(UTC)}
        if "query" in request.model_fields_set and request.query is not None:
            updates["query"] = self._required_text(request.query, "Eval item query")
        if "expected_terms" in request.model_fields_set and request.expected_terms is not None:
            updates["expected_terms"] = self._clean_required_list(request.expected_terms, "expected_terms")
        if "expected_document_ids" in request.model_fields_set and request.expected_document_ids is not None:
            updates["expected_document_ids"] = self._clean_optional_list(request.expected_document_ids)
        if "expected_chunk_ids" in request.model_fields_set and request.expected_chunk_ids is not None:
            updates["expected_chunk_ids"] = self._clean_optional_list(request.expected_chunk_ids)
        if "tags" in request.model_fields_set and request.tags is not None:
            updates["tags"] = self._clean_optional_list(request.tags)
        if "notes" in request.model_fields_set:
            updates["notes"] = self._optional_text(request.notes)

        updated_item = item.model_copy(update=updates)
        self.repository.save_eval_item(updated_item)
        return updated_item

    def delete_eval_item(self, dataset_id: str, item_id: str) -> bool:
        if self.get_eval_item(dataset_id, item_id) is None:
            return False

        self.repository.delete_eval_item(dataset_id, item_id)
        return True

    def save_eval_run(self, eval_run: dict[str, object]) -> dict[str, object]:
        self.repository.save_eval_run(eval_run)
        return eval_run

    def list_eval_runs(self, project_ids: frozenset[str] | None = None) -> list[dict[str, object]]:
        runs = [
            run
            for run in self.repository.list_eval_runs()
            if self._project_visible(_optional_project_id(run.get("project_id")), project_ids)
        ]

        return sorted(
            runs,
            key=lambda run: str(run.get("created_at") or ""),
            reverse=True,
        )

    def get_eval_run(self, run_id: str) -> dict[str, object] | None:
        for run in self.repository.list_eval_runs():
            if str(run.get("run_id") or "") == run_id:
                return run

        return None

    def list_documents_for_rag(self, project_ids: frozenset[str] | None = None) -> list[DocumentMetadata]:
        documents = self._read_documents()
        documents_changed = False

        for index, document in enumerate(documents):
            if project_ids is not None and (
                document.project_id is None or document.project_id not in project_ids
            ):
                continue

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

        if project_ids is None:
            return documents

        return [
            document
            for document in documents
            if document.project_id is not None and document.project_id in project_ids
        ]

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

    async def save_upload(self, file: UploadFile, project_id: str | None = None) -> DocumentMetadata:
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
            project_id=project_id,
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
        if self._is_text_upload(document):
            self._ingest_text_upload(document, content, created_at)
        elif self._is_pdf_upload(document):
            self._ingest_pdf_upload(document, content, created_at)

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
            if self._is_pdf_upload(document) and document.page_images:
                ocr_result = self._run_pdf_page_image_ocr(document, provider, now)
            else:
                ocr_result = provider.extract(document, self.get_file_path(document), now)
            document.ocr = ocr_result
            ocr_job_type = provider.job_type
            chunk_source = ocr_result.extracted_fields.get("chunk_source", provider.chunk_source)

            if ocr_result.status == OcrStatus.COMPLETED:
                new_chunks = self._build_chunks(
                    document.document_id,
                    ocr_result.text,
                    now,
                    source=chunk_source,
                    ocr_lines=ocr_result.lines,
                )
                if chunk_source == "pdf_page_ocr":
                    retained_chunks = [
                        chunk
                        for chunk in document.chunks
                        if chunk.source != "pdf_page_ocr" and chunk.source_type != "pdf_page_ocr"
                    ]
                    new_chunks = [
                        chunk.model_copy(
                            update={
                                "chunk_id": (
                                    f"{document.document_id}-chunk-"
                                    f"{len(retained_chunks) + chunk_index:03d}"
                                )
                            }
                        )
                        for chunk_index, chunk in enumerate(new_chunks, start=1)
                    ]
                    document.chunks = [*retained_chunks, *new_chunks]
                else:
                    document.chunks = new_chunks
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
                if chunk_source == "pdf_page_ocr":
                    document.chunks = [
                        chunk
                        for chunk in document.chunks
                        if chunk.source != "pdf_page_ocr" and chunk.source_type != "pdf_page_ocr"
                    ]
                else:
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

    def _run_pdf_page_image_ocr(
        self,
        document: DocumentMetadata,
        provider: OcrProvider,
        timestamp: datetime,
    ) -> OcrResult:
        page_lines: list[OcrTextLine] = []
        page_texts: list[str] = []
        failures: list[str] = []
        provider_name = getattr(provider, "provider_name", provider.chunk_source)

        for page_index, page_image in enumerate(document.page_images):
            page_path = self._get_page_image_path(page_image)
            attempts = page_image.ocr_attempts + 1

            if page_path is None:
                failure_reason = f"page_image_missing: {page_image.path}"
                document.page_images[page_index] = page_image.model_copy(
                    update={
                        "page_status": "ocr_failed",
                        "ocr_attempts": attempts,
                        "failure_reason": failure_reason,
                        "updated_at": timestamp,
                    }
                )
                failures.append(f"page {page_image.page_number}: {failure_reason}")
                continue

            running_page = page_image.model_copy(
                update={
                    "page_status": "ocr_running",
                    "ocr_attempts": attempts,
                    "failure_reason": None,
                    "updated_at": timestamp,
                }
            )
            page_document = document.model_copy(
                update={
                    "filename": Path(page_image.path).name,
                    "stored_filename": page_image.path,
                    "file_type": page_path.suffix.lstrip(".").lower() or "png",
                    "content_type": "image/png",
                    "size": page_path.stat().st_size,
                    "chunks": [],
                    "page_images": [],
                }
            )
            page_result = provider.extract(page_document, page_path, timestamp)

            if page_result.status != OcrStatus.COMPLETED:
                failure_reason = page_result.extracted_fields.get("error", "OCR failed")
                document.page_images[page_index] = running_page.model_copy(
                    update={
                        "page_status": "ocr_failed",
                        "ocr_text": page_result.text,
                        "ocr_blocks": [],
                        "ocr_provider": provider_name,
                        "failure_reason": failure_reason,
                        "metadata": {
                            "ocr_provider": provider_name,
                            "error_code": page_result.extracted_fields.get("error_code", "ocr_failed"),
                        },
                        "updated_at": timestamp,
                    }
                )
                failures.append(f"page {page_image.page_number}: {failure_reason}")
                continue

            normalized_lines = self._normalize_page_ocr_lines(
                page_result,
                page_image,
                provider_name,
            )
            page_text = "\n".join(line.text for line in normalized_lines).strip()
            if not page_text:
                page_text = page_result.text.strip()

            document.page_images[page_index] = running_page.model_copy(
                update={
                    "page_status": "ocr_succeeded",
                    "ocr_text": page_text,
                    "ocr_blocks": normalized_lines,
                    "ocr_provider": provider_name,
                    "failure_reason": None,
                    "metadata": {
                        "ocr_provider": provider_name,
                        "line_count": str(len(normalized_lines)),
                        "source_type": running_page.source_type,
                    },
                    "updated_at": timestamp,
                }
            )
            page_texts.append(page_text)
            page_lines.extend(normalized_lines)

        if failures:
            return OcrResult(
                status=OcrStatus.FAILED,
                text="\n".join(page_texts),
                extracted_fields={
                    "provider": provider_name,
                    "chunk_source": "pdf_page_ocr",
                    "source_type": "pdf_page_ocr",
                    "content_source": "pdf_scanned_ocr",
                    "error_code": "pdf_page_ocr_failed",
                    "error": "; ".join(failures),
                    "failed_page_count": str(len(failures)),
                    "page_count": str(len(document.page_images)),
                },
                lines=page_lines,
                updated_at=timestamp,
            )

        return OcrResult(
            status=OcrStatus.COMPLETED,
            text="\n\n".join(page_text for page_text in page_texts if page_text),
            extracted_fields={
                "provider": provider_name,
                "chunk_source": "pdf_page_ocr",
                "source_type": "pdf_page_ocr",
                "content_source": "pdf_scanned_ocr",
                "page_count": str(len(document.page_images)),
                "line_count": str(len(page_lines)),
            },
            lines=page_lines,
            updated_at=timestamp,
        )

    def _get_page_image_path(self, page_image: PdfPageImage) -> Path | None:
        data_root = self.data_dir.resolve()
        image_path = (data_root / page_image.path).resolve()

        try:
            image_path.relative_to(data_root)
        except ValueError:
            return None

        if not image_path.is_file():
            return None

        return image_path

    def _normalize_page_ocr_lines(
        self,
        page_result: OcrResult,
        page_image: PdfPageImage,
        provider_name: str,
    ) -> list[OcrTextLine]:
        if page_result.lines:
            return [
                line.model_copy(
                    update={
                        "page_number": page_image.page_number,
                        "metadata": {
                            **line.metadata,
                            "ocr_provider": provider_name,
                            "page_image_id": page_image.image_id,
                            "page_image_path": page_image.path,
                            "content_source": "pdf_scanned_ocr",
                        },
                    }
                )
                for line in page_result.lines
                if line.text.strip()
            ]

        lines: list[OcrTextLine] = []
        for line_index, raw_line in enumerate(page_result.text.splitlines(), start=1):
            text = raw_line.strip()
            if not text:
                continue

            lines.append(
                OcrTextLine(
                    text=text,
                    page_number=page_image.page_number,
                    metadata={
                        "ocr_provider": provider_name,
                        "line_index": str(line_index),
                        "page_image_id": page_image.image_id,
                        "page_image_path": page_image.path,
                        "content_source": "pdf_scanned_ocr",
                    },
                )
            )

        return lines

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

    def _read_documents(self) -> list[DocumentMetadata]:
        self._ensure_storage()
        return self.repository.list_documents()

    def _ensure_agent_run_storage(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _read_agent_runs(self) -> list[AgentRun]:
        self._ensure_agent_run_storage()
        return self.repository.list_agent_runs()

    def _write_agent_runs(self, agent_runs: list[AgentRun]) -> None:
        self.repository.write_agent_runs(agent_runs)

    def _write_documents(self, documents: list[DocumentMetadata]) -> None:
        self.repository.write_documents(documents)

    def _project_visible(self, project_id: str | None, project_ids: frozenset[str] | None) -> bool:
        if project_ids is None:
            return True

        return project_id is not None and project_id in project_ids

    def _required_text(self, value: str, label: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError(f"{label} cannot be blank.")

        return text

    def _optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None

        text = value.strip()
        return text or None

    def _clean_required_list(self, values: list[str], label: str) -> list[str]:
        cleaned = self._clean_optional_list(values)
        if not cleaned:
            raise ValueError(f"{label} requires at least one value.")

        return cleaned

    def _clean_optional_list(self, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for value in values:
            text = value.strip()
            if text and text not in seen:
                cleaned.append(text)
                seen.add(text)

        return cleaned

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
        chunk_metadata: dict[str, str] | None = None,
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
        metadata = chunk_metadata or {"origin": "ocr_text", "provider": source}

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
                        metadata=metadata,
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
                metadata=metadata,
            )
        )

        return chunks

    def _is_text_upload(self, document: DocumentMetadata) -> bool:
        return document.file_type.lower() == "txt"

    def _is_pdf_upload(self, document: DocumentMetadata) -> bool:
        return document.file_type.lower() == "pdf" or document.content_type.lower() == "application/pdf"

    def _ingest_text_upload(self, document: DocumentMetadata, content: bytes, timestamp: datetime) -> None:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            document.status = DocumentStatus.FAILED
            document.processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.PENDING,
                indexing=ProcessingStepStatus.FAILED,
                ready=False,
                failed_reason="Text upload must be UTF-8.",
                updated_at=timestamp,
            )
            self._record_job(
                document,
                ProcessingJobType.TEXT_INGESTION,
                ProcessingStepStatus.FAILED,
                timestamp,
                error_message="Text upload must be UTF-8.",
            )
            return

        normalized_text = self._normalize_text_upload(text)
        if not normalized_text:
            document.status = DocumentStatus.FAILED
            document.processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.PENDING,
                indexing=ProcessingStepStatus.FAILED,
                ready=False,
                failed_reason="Text upload was empty.",
                updated_at=timestamp,
            )
            self._record_job(
                document,
                ProcessingJobType.TEXT_INGESTION,
                ProcessingStepStatus.FAILED,
                timestamp,
                error_message="Text upload was empty.",
            )
            return

        document.chunks = self._build_chunks(
            document.document_id,
            normalized_text,
            timestamp,
            source="text_upload",
            chunk_metadata={
                "origin": "uploaded_text",
                "content_source": "text_upload",
                "source_router": "text_upload",
            },
        )
        document.status = DocumentStatus.READY
        document.processing = ProcessingStatus(
            upload=ProcessingStepStatus.COMPLETED,
            ocr=ProcessingStepStatus.PENDING,
            indexing=ProcessingStepStatus.COMPLETED,
            ready=True,
            updated_at=timestamp,
        )
        self._record_job(
            document,
            ProcessingJobType.TEXT_INGESTION,
            ProcessingStepStatus.COMPLETED,
            timestamp,
        )
        self._record_job(
            document,
            ProcessingJobType.LOCAL_INDEXING,
            ProcessingStepStatus.COMPLETED,
            timestamp,
        )

    def _normalize_text_upload(self, text: str) -> str:
        lines = []
        for line in text.splitlines():
            clean_line = re.sub(r"\s+", " ", line.strip())
            if clean_line:
                lines.append(clean_line)

        return "\n".join(lines)

    def _ingest_pdf_upload(self, document: DocumentMetadata, content: bytes, timestamp: datetime) -> None:
        try:
            page_count, pages = self._extract_pdf_text_pages(content)
        except Exception as exc:
            message = f"pdf_text_extraction_failed: {exc}"
            document.status = DocumentStatus.FAILED
            document.processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.PENDING,
                indexing=ProcessingStepStatus.FAILED,
                ready=False,
                failed_reason=message,
                updated_at=timestamp,
            )
            self._record_job(
                document,
                ProcessingJobType.PDF_TEXT_EXTRACTION,
                ProcessingStepStatus.FAILED,
                timestamp,
                error_message=message,
            )
            return

        if page_count < 1:
            message = "pdf_invalid: PDF has no pages."
            document.status = DocumentStatus.FAILED
            document.chunks = []
            document.processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.PENDING,
                indexing=ProcessingStepStatus.FAILED,
                ready=False,
                failed_reason=message,
                updated_at=timestamp,
            )
            self._record_job(
                document,
                ProcessingJobType.PDF_TEXT_EXTRACTION,
                ProcessingStepStatus.FAILED,
                timestamp,
                error_message=message,
            )
            return

        text_page_numbers = {page_number for page_number, _ in pages}
        scanned_page_numbers = [
            page_number
            for page_number in range(1, page_count + 1)
            if page_number not in text_page_numbers
        ]

        if scanned_page_numbers:
            source_type = "pdf_scanned_pending_ocr" if not pages else "pdf_mixed_pending_ocr"
            self._record_job(
                document,
                ProcessingJobType.PDF_TEXT_EXTRACTION,
                ProcessingStepStatus.COMPLETED,
                timestamp,
            )
            rendered = self._render_pdf_page_images(
                document,
                content,
                scanned_page_numbers,
                source_type,
                timestamp,
            )
            if not rendered:
                return

        if not pages:
            message = (
                "pdf_scanned_pending_ocr: PDF text layer is empty; "
                f"rendered {len(document.page_images)} page image(s); OCR worker is required."
            )
            document.status = DocumentStatus.UPLOADED
            document.chunks = []
            document.processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.PENDING,
                indexing=ProcessingStepStatus.PENDING,
                ready=False,
                failed_reason=message,
                updated_at=timestamp,
            )
            return

        if scanned_page_numbers:
            document.chunks = self._build_pdf_text_chunks(document.document_id, pages, timestamp)
            message = (
                "pdf_mixed_pending_ocr: PDF has text-native and scanned pages; "
                f"rendered {len(document.page_images)} scanned page image(s); OCR worker is required."
            )
            document.status = DocumentStatus.UPLOADED
            document.processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.PENDING,
                indexing=ProcessingStepStatus.PENDING,
                ready=False,
                failed_reason=message,
                updated_at=timestamp,
            )
            return

        document.chunks = self._build_pdf_text_chunks(document.document_id, pages, timestamp)
        document.status = DocumentStatus.READY
        document.processing = ProcessingStatus(
            upload=ProcessingStepStatus.COMPLETED,
            ocr=ProcessingStepStatus.PENDING,
            indexing=ProcessingStepStatus.COMPLETED,
            ready=True,
            updated_at=timestamp,
        )
        self._record_job(
            document,
            ProcessingJobType.PDF_TEXT_EXTRACTION,
            ProcessingStepStatus.COMPLETED,
            timestamp,
        )
        self._record_job(
            document,
            ProcessingJobType.LOCAL_INDEXING,
            ProcessingStepStatus.COMPLETED,
            timestamp,
        )

    def _render_pdf_page_images(
        self,
        document: DocumentMetadata,
        content: bytes,
        page_numbers: list[int],
        source_type: str,
        timestamp: datetime,
    ) -> bool:
        try:
            rendered_pages = self.pdf_renderer.render_pages(
                content,
                document.document_id,
                page_numbers,
                timestamp,
            )
        except PdfRenderingError as exc:
            message = str(exc)
            document.status = DocumentStatus.FAILED
            document.chunks = []
            document.page_images = []
            document.processing = ProcessingStatus(
                upload=ProcessingStepStatus.COMPLETED,
                ocr=ProcessingStepStatus.PENDING,
                indexing=ProcessingStepStatus.FAILED,
                ready=False,
                failed_reason=message,
                updated_at=timestamp,
            )
            self._record_job(
                document,
                ProcessingJobType.PDF_RENDERING,
                ProcessingStepStatus.FAILED,
                timestamp,
                error_message=message,
            )
            return False

        document.page_images = [
            PdfPageImage(
                image_id=page.image_id,
                document_id=document.document_id,
                page_number=page.page_number,
                path=page.path,
                width=page.width,
                height=page.height,
                dpi=page.dpi,
                checksum=page.checksum,
                page_status="rendered",
                source_type=source_type,
                created_at=page.created_at,
            )
            for page in rendered_pages
        ]
        self._record_job(
            document,
            ProcessingJobType.PDF_RENDERING,
            ProcessingStepStatus.COMPLETED,
            timestamp,
        )
        return True

    def _extract_pdf_text_pages(self, content: bytes) -> tuple[int, list[tuple[int, str]]]:
        reader = PdfReader(BytesIO(content))
        pages: list[tuple[int, str]] = []

        for page_index, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            normalized_text = self._normalize_text_upload(raw_text)
            if normalized_text:
                pages.append((page_index, normalized_text))

        return len(reader.pages), pages

    def _build_pdf_text_chunks(
        self,
        document_id: str,
        pages: list[tuple[int, str]],
        created_at: datetime,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        max_chunk_size = 360

        for page_number, text in pages:
            current_lines: list[str] = []
            current_size = 0

            for line in text.splitlines():
                clean_line = line.strip()
                if not clean_line:
                    continue

                separator_size = 1 if current_lines else 0
                next_size = current_size + len(clean_line) + separator_size
                if current_lines and next_size > max_chunk_size:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{document_id}-chunk-{len(chunks) + 1:03d}",
                            document_id=document_id,
                            text="\n".join(current_lines),
                            source="pdf_text",
                            created_at=created_at,
                            page_number=page_number,
                            source_type="pdf_text",
                            metadata={
                                "origin": "pdf_text",
                                "content_source": "pdf_text",
                                "source_router": "pdf_text",
                                "page_number": str(page_number),
                            },
                        )
                    )
                    current_lines = []
                    current_size = 0

                current_lines.append(clean_line)
                current_size += len(clean_line) + separator_size

            if current_lines:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{document_id}-chunk-{len(chunks) + 1:03d}",
                        document_id=document_id,
                        text="\n".join(current_lines),
                        source="pdf_text",
                        created_at=created_at,
                        page_number=page_number,
                        source_type="pdf_text",
                        metadata={
                            "origin": "pdf_text",
                            "content_source": "pdf_text",
                            "source_router": "pdf_text",
                            "page_number": str(page_number),
                        },
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


def _optional_project_id(value: object) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None
