from datetime import datetime
from pathlib import Path
from typing import Protocol

from app.schemas.documents import DocumentMetadata, OcrResult, OcrStatus


class OcrProvider(Protocol):
    chunk_source: str

    def extract(
        self,
        document: DocumentMetadata,
        file_path: Path | None,
        extracted_at: datetime,
    ) -> OcrResult:
        pass


class MockOcrProvider:
    chunk_source = "ocr_mock"
    text_file_types = {"csv", "md", "txt"}

    def extract(
        self,
        document: DocumentMetadata,
        file_path: Path | None,
        extracted_at: datetime,
    ) -> OcrResult:
        ocr_lines = [
            f"Mock OCR result for {document.filename}",
            f"Document ID: {document.document_id}",
            f"File type: {document.file_type}",
            f"Content type: {document.content_type}",
            f"Size: {document.size} bytes",
        ]

        if (
            file_path is not None
            and (document.content_type.startswith("text/") or document.file_type in self.text_file_types)
        ):
            try:
                uploaded_text = file_path.read_text(encoding="utf-8").strip()
            except UnicodeDecodeError:
                uploaded_text = ""

            if uploaded_text:
                ocr_lines.extend(["Uploaded text content:", uploaded_text[:4000]])

        return OcrResult(
            status=OcrStatus.COMPLETED,
            text="\n".join(ocr_lines),
            extracted_fields={
                "filename": document.filename,
                "file_type": document.file_type,
                "content_type": document.content_type,
                "size_bytes": str(document.size),
            },
            updated_at=extracted_at,
        )
