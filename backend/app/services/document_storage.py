from datetime import UTC, datetime
import json
from pathlib import Path
import re
from uuid import uuid4

from fastapi import UploadFile

from app.schemas.documents import DocumentMetadata, DocumentStatus, OcrResult, OcrStatus


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

    def run_mock_ocr(self, document_id: str) -> OcrResult | None:
        documents = self._read_documents()

        for index, document in enumerate(documents):
            if document.document_id != document_id:
                continue

            ocr_result = OcrResult(
                status=OcrStatus.COMPLETED,
                text="\n".join(
                    [
                        f"Mock OCR result for {document.filename}",
                        f"Document ID: {document.document_id}",
                        f"File type: {document.file_type}",
                        f"Content type: {document.content_type}",
                        f"Size: {document.size} bytes",
                    ]
                ),
                extracted_fields={
                    "filename": document.filename,
                    "file_type": document.file_type,
                    "content_type": document.content_type,
                    "size_bytes": str(document.size),
                },
                updated_at=datetime.now(UTC),
            )
            document.ocr = ocr_result
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
        temp_path = self.metadata_path.with_suffix(".json.tmp")
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temp_path.replace(self.metadata_path)

    def _safe_filename(self, filename: str) -> str:
        name = Path(filename.replace("\\", "/")).name
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")

        return name or "uploaded-file"
