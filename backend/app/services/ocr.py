from datetime import datetime
from pathlib import Path
from typing import Protocol

from app.schemas.documents import DocumentMetadata, OcrResult, OcrStatus, ProcessingJobType


class OcrProvider(Protocol):
    provider_name: str
    chunk_source: str
    job_type: ProcessingJobType

    def extract(
        self,
        document: DocumentMetadata,
        file_path: Path | None,
        extracted_at: datetime,
    ) -> OcrResult:
        pass


class MockOcrProvider:
    provider_name = "mock"
    chunk_source = "ocr_mock"
    job_type = ProcessingJobType.OCR_MOCK
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


class PaddleOcrProvider:
    provider_name = "paddleocr"
    chunk_source = "ocr_paddleocr"
    job_type = ProcessingJobType.OCR_REAL
    supported_file_types = {"bmp", "jpeg", "jpg", "png", "tif", "tiff", "webp"}

    def __init__(self, language: str = "en") -> None:
        self.language = language
        self._engine = None

    def extract(
        self,
        document: DocumentMetadata,
        file_path: Path | None,
        extracted_at: datetime,
    ) -> OcrResult:
        if file_path is None:
            return self._failed_result(
                "paddleocr_file_missing",
                "Document file not found for PaddleOCR provider.",
                extracted_at,
            )

        if not document.content_type.startswith("image/") and document.file_type not in self.supported_file_types:
            return self._failed_result(
                "paddleocr_unsupported_file_type",
                "PaddleOCR Phase 07 adapter supports image files only; PDF rendering is out of scope.",
                extracted_at,
            )

        try:
            engine = self._load_engine()
        except ImportError:
            return self._failed_result(
                "paddleocr_dependency_missing",
                "PaddleOCR dependency is not installed. Install backend with the real OCR extra to use provider-selected OCR.",
                extracted_at,
            )
        except Exception as exc:
            return self._failed_result(
                "paddleocr_initialization_failed",
                f"PaddleOCR initialization failed: {exc}",
                extracted_at,
            )

        try:
            try:
                raw_result = engine.ocr(str(file_path), cls=True)
            except TypeError:
                raw_result = engine.ocr(str(file_path))
        except Exception as exc:
            return self._failed_result(
                "paddleocr_runtime_failed",
                f"PaddleOCR failed while processing the document: {exc}",
                extracted_at,
            )

        lines: list[str] = []
        confidences: list[float] = []

        for page_result in raw_result or []:
            if not page_result:
                continue

            line_items = page_result
            if (
                isinstance(page_result, (list, tuple))
                and len(page_result) >= 2
                and isinstance(page_result[1], (list, tuple))
                and page_result[1]
                and isinstance(page_result[1][0], str)
            ):
                line_items = [page_result]

            for item in line_items:
                if (
                    not isinstance(item, (list, tuple))
                    or len(item) < 2
                    or not isinstance(item[1], (list, tuple))
                    or not item[1]
                ):
                    continue

                text = str(item[1][0]).strip()
                if not text:
                    continue

                lines.append(text)
                if len(item[1]) > 1:
                    try:
                        confidences.append(float(item[1][1]))
                    except (TypeError, ValueError):
                        pass

        if not lines:
            return self._failed_result(
                "paddleocr_empty_result",
                "PaddleOCR returned no recognized text.",
                extracted_at,
            )

        extracted_fields = {
            "provider": "paddleocr",
            "filename": document.filename,
            "line_count": str(len(lines)),
        }

        if confidences:
            extracted_fields["average_confidence"] = f"{sum(confidences) / len(confidences):.4f}"

        return OcrResult(
            status=OcrStatus.COMPLETED,
            text="\n".join(lines),
            extracted_fields=extracted_fields,
            updated_at=extracted_at,
        )

    def _load_engine(self):
        if self._engine is None:
            from paddleocr import PaddleOCR

            self._engine = PaddleOCR(use_angle_cls=True, lang=self.language)

        return self._engine

    def _failed_result(self, error_code: str, message: str, extracted_at: datetime) -> OcrResult:
        return OcrResult(
            status=OcrStatus.FAILED,
            text="",
            extracted_fields={
                "provider": "paddleocr",
                "error_code": error_code,
                "error": message,
            },
            updated_at=extracted_at,
        )
