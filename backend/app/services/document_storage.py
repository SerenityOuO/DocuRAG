from datetime import UTC, datetime
import json
from pathlib import Path
import re
from uuid import uuid4

from fastapi import UploadFile

from app.schemas.documents import (
    DocumentChunk,
    DocumentMetadata,
    DocumentStatus,
    OcrResult,
    OcrStatus,
)
from app.schemas.rag import RetrievedChunk
from app.services.ocr import OcrProvider


class DocumentStorage:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.upload_dir = data_dir / "uploads"
        self.metadata_path = data_dir / "documents.json"

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

    def search_chunks(self, query: str, top_k: int) -> list[RetrievedChunk]:
        query_terms = self._tokenize(query)

        if not query_terms:
            return []

        matches: list[RetrievedChunk] = []
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
                )
                documents[index] = document
                documents_changed = True

            for chunk in document.chunks:
                chunk_terms = self._tokenize(chunk.text)
                score = sum(chunk_terms.count(term) for term in query_terms)

                if score <= 0:
                    continue

                matches.append(
                    RetrievedChunk(
                        **chunk.model_dump(),
                        filename=document.filename,
                        score=float(score),
                    )
                )

        if documents_changed:
            self._write_documents(documents)

        return sorted(
            matches,
            key=lambda chunk: (-chunk.score, -chunk.created_at.timestamp(), chunk.chunk_id),
        )[:top_k]

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

        document = DocumentMetadata(
            document_id=document_id,
            project_id=None,
            filename=filename,
            stored_filename=stored_filename,
            file_type=Path(filename).suffix.lstrip(".").lower() or "unknown",
            content_type=file.content_type or "application/octet-stream",
            size=len(content),
            status=DocumentStatus.UPLOADED,
            created_at=datetime.now(UTC),
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
            document.chunks = self._build_chunks(
                document.document_id,
                ocr_result.text,
                now,
                source=provider.chunk_source,
            )
            document.status = DocumentStatus.READY
            documents[index] = document
            self._write_documents(documents)

            return ocr_result

        return None

    def _ensure_storage(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        if not self.metadata_path.exists():
            self.metadata_path.write_text("[]\n", encoding="utf-8")

    def _read_documents(self) -> list[DocumentMetadata]:
        self._ensure_storage()

        raw_documents = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        return [DocumentMetadata.model_validate(raw_document) for raw_document in raw_documents]

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
    ) -> list[DocumentChunk]:
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
                )
            )

        return chunks

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())
