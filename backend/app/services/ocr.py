from datetime import datetime
from pathlib import Path
import sys
from typing import Protocol

from app.schemas.documents import BoundingBox, DocumentMetadata, OcrResult, OcrStatus, OcrTextLine, ProcessingJobType


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


class PaddleOcrUnsupportedPythonError(RuntimeError):
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
        except PaddleOcrUnsupportedPythonError as exc:
            return self._failed_result(
                "paddleocr_python_unsupported",
                str(exc),
                extracted_at,
            )
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

        ocr_lines: list[OcrTextLine] = []
        confidences: list[float] = []

        raw_pages = raw_result or []
        direct_line_items = all(self._is_line_item(item) for item in raw_pages)

        for page_index, page_result in enumerate(raw_pages, start=1):
            if not page_result:
                continue

            line_items = page_result
            page_number = 1 if direct_line_items else page_index
            if self._is_line_item(page_result):
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

                confidence = None
                if len(item[1]) > 1:
                    try:
                        confidence = float(item[1][1])
                    except (TypeError, ValueError):
                        confidence = None

                if confidence is not None and 0 <= confidence <= 1:
                    confidences.append(confidence)
                else:
                    confidence = None

                bbox = None
                if isinstance(item[0], (list, tuple)):
                    try:
                        xs = [float(point[0]) for point in item[0] if isinstance(point, (list, tuple)) and len(point) >= 2]
                        ys = [float(point[1]) for point in item[0] if isinstance(point, (list, tuple)) and len(point) >= 2]
                        if xs and ys:
                            bbox = BoundingBox(
                                x_min=min(xs),
                                y_min=min(ys),
                                x_max=max(xs),
                                y_max=max(ys),
                            )
                    except (TypeError, ValueError):
                        bbox = None

                ocr_lines.append(
                    OcrTextLine(
                        text=text,
                        page_number=page_number,
                        bbox=bbox,
                        confidence=confidence,
                        metadata={
                            "ocr_provider": "paddleocr",
                            "line_index": str(len(ocr_lines) + 1),
                        },
                    )
                )

        if not ocr_lines:
            return self._failed_result(
                "paddleocr_empty_result",
                "PaddleOCR returned no recognized text.",
                extracted_at,
            )

        extracted_fields = {
            "provider": "paddleocr",
            "chunk_source": self.chunk_source,
            "filename": document.filename,
            "line_count": str(len(ocr_lines)),
        }

        if confidences:
            extracted_fields["average_confidence"] = f"{sum(confidences) / len(confidences):.4f}"

        return OcrResult(
            status=OcrStatus.COMPLETED,
            text="\n".join(line.text for line in ocr_lines),
            extracted_fields=extracted_fields,
            lines=ocr_lines,
            updated_at=extracted_at,
        )

    def _load_engine(self):
        if self._engine is None:
            if sys.version_info >= (3, 13):
                version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                raise PaddleOcrUnsupportedPythonError(
                    "PaddleOCR local runtime is supported only on Python 3.11 or 3.12 in this project. "
                    f"Current Python is {version}. Install Python 3.12, then run "
                    'py -3.12 -m pip install -e ".[dev,real-ocr]" from the backend directory.'
                )

            from paddleocr import PaddleOCR

            self._engine = PaddleOCR(use_angle_cls=True, lang=self.language)

        return self._engine

    def _is_line_item(self, value: object) -> bool:
        return (
            isinstance(value, (list, tuple))
            and len(value) >= 2
            and isinstance(value[1], (list, tuple))
            and bool(value[1])
            and isinstance(value[1][0], str)
        )

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
