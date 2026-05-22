from datetime import datetime
import logging
import os
from pathlib import Path
import sys
from time import perf_counter
from typing import Protocol

from app.schemas.documents import BoundingBox, DocumentMetadata, OcrResult, OcrStatus, OcrTextLine, ProcessingJobType


logger = logging.getLogger(__name__)


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


class PaddleOcrGpuRequiredError(RuntimeError):
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

    def __init__(
        self,
        language: str = "ch",
        ocr_version: str = "PP-OCRv4",
        det_model_name: str = "PP-OCRv4_mobile_det",
        rec_model_name: str = "PP-OCRv4_mobile_rec",
        cls_model_name: str = "ch_ppocr_mobile_v2.0_cls",
        det_model_dir: str | None = None,
        rec_model_dir: str | None = None,
        cls_model_dir: str | None = None,
        use_angle_cls: bool = False,
        det_limit_side_len: int = 960,
        rec_batch_num: int = 6,
    ) -> None:
        self.language = language
        self.ocr_version = ocr_version
        self.det_model_name = det_model_name
        self.rec_model_name = rec_model_name
        self.cls_model_name = cls_model_name
        self.det_model_dir = self._resolve_model_dir(det_model_dir, "det", "ch", "ch_PP-OCRv4_det_infer")
        self.rec_model_dir = self._resolve_model_dir(rec_model_dir, "rec", "ch", "ch_PP-OCRv4_rec_infer")
        self.cls_model_dir = self._resolve_model_dir(cls_model_dir, "cls", "ch", "ch_ppocr_mobile_v2.0_cls_infer")
        self.use_angle_cls = use_angle_cls
        self.det_limit_side_len = det_limit_side_len
        self.rec_batch_num = rec_batch_num
        self._engine = None
        self._engine_preload_duration_ms: float | None = None

    def preload(self) -> None:
        already_loaded = self._engine is not None
        started_at = perf_counter()
        self._load_engine()
        duration_ms = (perf_counter() - started_at) * 1000

        if not already_loaded:
            self._engine_preload_duration_ms = duration_ms

        logger.info(
            "PaddleOCR engine preload completed: already_loaded=%s duration_ms=%.2f use_angle_cls=%s det_limit_side_len=%s rec_batch_num=%s",
            already_loaded,
            duration_ms,
            self.use_angle_cls,
            self.det_limit_side_len,
            self.rec_batch_num,
        )

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

        total_started_at = perf_counter()
        engine_preloaded_before_request = self._engine is not None
        engine_load_started_at = perf_counter()
        try:
            engine = self._load_engine()
        except PaddleOcrUnsupportedPythonError as exc:
            engine_load_ms = (perf_counter() - engine_load_started_at) * 1000
            return self._failed_result(
                "paddleocr_python_unsupported",
                str(exc),
                extracted_at,
                self._timing_fields(
                    engine_preloaded_before_request=engine_preloaded_before_request,
                    engine_load_ms=engine_load_ms,
                    total_ms=(perf_counter() - total_started_at) * 1000,
                ),
            )
        except PaddleOcrGpuRequiredError as exc:
            engine_load_ms = (perf_counter() - engine_load_started_at) * 1000
            return self._failed_result(
                "paddleocr_gpu_required",
                str(exc),
                extracted_at,
                self._timing_fields(
                    engine_preloaded_before_request=engine_preloaded_before_request,
                    engine_load_ms=engine_load_ms,
                    total_ms=(perf_counter() - total_started_at) * 1000,
                ),
            )
        except ImportError:
            engine_load_ms = (perf_counter() - engine_load_started_at) * 1000
            return self._failed_result(
                "paddleocr_dependency_missing",
                "PaddleOCR GPU dependency is not installed. Install the CUDA PaddlePaddle wheel and backend real OCR extra to use provider-selected OCR.",
                extracted_at,
                self._timing_fields(
                    engine_preloaded_before_request=engine_preloaded_before_request,
                    engine_load_ms=engine_load_ms,
                    total_ms=(perf_counter() - total_started_at) * 1000,
                ),
            )
        except Exception as exc:
            engine_load_ms = (perf_counter() - engine_load_started_at) * 1000
            return self._failed_result(
                "paddleocr_initialization_failed",
                f"PaddleOCR initialization failed: {exc}",
                extracted_at,
                self._timing_fields(
                    engine_preloaded_before_request=engine_preloaded_before_request,
                    engine_load_ms=engine_load_ms,
                    total_ms=(perf_counter() - total_started_at) * 1000,
                ),
            )
        engine_load_ms = (perf_counter() - engine_load_started_at) * 1000

        if not engine_preloaded_before_request and self._engine_preload_duration_ms is None:
            self._engine_preload_duration_ms = engine_load_ms

        inference_started_at = perf_counter()
        try:
            try:
                raw_result = engine.ocr(str(file_path), cls=self.use_angle_cls)
            except TypeError:
                raw_result = engine.ocr(str(file_path))
        except Exception as exc:
            inference_ms = (perf_counter() - inference_started_at) * 1000
            return self._failed_result(
                "paddleocr_runtime_failed",
                f"PaddleOCR failed while processing the document: {exc}",
                extracted_at,
                self._timing_fields(
                    engine_preloaded_before_request=engine_preloaded_before_request,
                    engine_load_ms=engine_load_ms,
                    inference_ms=inference_ms,
                    total_ms=(perf_counter() - total_started_at) * 1000,
                ),
            )
        inference_ms = (perf_counter() - inference_started_at) * 1000

        normalization_started_at = perf_counter()
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
                            "ocr_language": self.language,
                            "ocr_version": self.ocr_version,
                            "det_model": self.det_model_name,
                            "rec_model": self.rec_model_name,
                            "cls_model": self.cls_model_name,
                            "use_angle_cls": str(self.use_angle_cls).lower(),
                            "line_index": str(len(ocr_lines) + 1),
                        },
                    )
                )

        normalization_ms = (perf_counter() - normalization_started_at) * 1000
        total_ms = (perf_counter() - total_started_at) * 1000
        timing_fields = self._timing_fields(
            engine_preloaded_before_request=engine_preloaded_before_request,
            engine_load_ms=engine_load_ms,
            inference_ms=inference_ms,
            normalization_ms=normalization_ms,
            total_ms=total_ms,
        )

        if not ocr_lines:
            return self._failed_result(
                "paddleocr_empty_result",
                "PaddleOCR returned no recognized text.",
                extracted_at,
                timing_fields,
            )

        extracted_fields = {
            "provider": "paddleocr",
            "chunk_source": self.chunk_source,
            "filename": document.filename,
            "line_count": str(len(ocr_lines)),
            "ocr_language": self.language,
            "ocr_version": self.ocr_version,
            "det_model": self.det_model_name,
            "rec_model": self.rec_model_name,
            "cls_model": self.cls_model_name,
            "det_model_dir": self.det_model_dir,
            "rec_model_dir": self.rec_model_dir,
            "cls_model_dir": self.cls_model_dir,
            "use_angle_cls": str(self.use_angle_cls).lower(),
            "det_limit_side_len": str(self.det_limit_side_len),
            "rec_batch_num": str(self.rec_batch_num),
            **timing_fields,
        }

        if confidences:
            extracted_fields["average_confidence"] = f"{sum(confidences) / len(confidences):.4f}"

        logger.info(
            "PaddleOCR OCR completed: filename=%s lines=%s engine_preloaded_before_request=%s engine_load_ms=%.2f inference_ms=%.2f normalization_ms=%.2f total_ms=%.2f use_angle_cls=%s det_limit_side_len=%s",
            document.filename,
            len(ocr_lines),
            engine_preloaded_before_request,
            engine_load_ms,
            inference_ms,
            normalization_ms,
            total_ms,
            self.use_angle_cls,
            self.det_limit_side_len,
        )

        return OcrResult(
            status=OcrStatus.COMPLETED,
            text="\n".join(line.text for line in ocr_lines),
            extracted_fields=extracted_fields,
            lines=ocr_lines,
            updated_at=extracted_at,
        )

    def _load_engine(self):
        if self._engine is None:
            if (sys.version_info.major, sys.version_info.minor) != (3, 12):
                version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                raise PaddleOcrUnsupportedPythonError(
                    "PaddleOCR local runtime is supported only on Python 3.12 in this project. "
                    f"Current Python is {version}. Install Python 3.12, then install "
                    "paddlepaddle-gpu from the CUDA 12.9 stable index and run "
                    'py -3.12 -m pip install -e ".[dev,real-ocr]" from the backend directory.'
                )

            import paddle

            if not paddle.device.is_compiled_with_cuda():
                raise PaddleOcrGpuRequiredError(
                    "DocuRAG real OCR requires a CUDA-enabled PaddlePaddle runtime. "
                    "Install paddlepaddle-gpu from the CUDA 12.9 stable index before using provider-selected OCR."
                )

            try:
                paddle.utils.run_check()
            except Exception as exc:
                raise PaddleOcrGpuRequiredError(f"PaddlePaddle CUDA runtime check failed: {exc}") from exc

            from paddleocr import PaddleOCR

            self._engine = PaddleOCR(
                use_angle_cls=self.use_angle_cls,
                lang=self.language,
                ocr_version=self.ocr_version,
                use_gpu=True,
                det_model_dir=self.det_model_dir,
                rec_model_dir=self.rec_model_dir,
                cls_model_dir=self.cls_model_dir,
                det_limit_side_len=self.det_limit_side_len,
                rec_batch_num=self.rec_batch_num,
            )

        return self._engine

    def _resolve_model_dir(self, configured_dir: str | None, category: str, language: str, inference_dir: str) -> str:
        if configured_dir:
            return str(Path(configured_dir).expanduser())

        model_root = Path(os.environ.get("PADDLEOCR_HOME", Path.home() / ".paddleocr")).expanduser()
        return str(model_root / "whl" / category / language / inference_dir)

    def _is_line_item(self, value: object) -> bool:
        return (
            isinstance(value, (list, tuple))
            and len(value) >= 2
            and isinstance(value[1], (list, tuple))
            and bool(value[1])
            and isinstance(value[1][0], str)
        )

    def _timing_fields(
        self,
        *,
        engine_preloaded_before_request: bool,
        engine_load_ms: float,
        total_ms: float,
        inference_ms: float | None = None,
        normalization_ms: float | None = None,
    ) -> dict[str, str]:
        fields = {
            "engine_preloaded_before_request": str(engine_preloaded_before_request).lower(),
            "timing_engine_load_ms": f"{engine_load_ms:.2f}",
            "timing_total_ms": f"{total_ms:.2f}",
        }

        if self._engine_preload_duration_ms is not None:
            fields["timing_engine_preload_ms"] = f"{self._engine_preload_duration_ms:.2f}"

        if inference_ms is not None:
            fields["timing_inference_ms"] = f"{inference_ms:.2f}"

        if normalization_ms is not None:
            fields["timing_normalization_ms"] = f"{normalization_ms:.2f}"

        return fields

    def _failed_result(
        self,
        error_code: str,
        message: str,
        extracted_at: datetime,
        extra_fields: dict[str, str] | None = None,
    ) -> OcrResult:
        return OcrResult(
            status=OcrStatus.FAILED,
            text="",
            extracted_fields={
                "provider": "paddleocr",
                "error_code": error_code,
                "error": message,
                **(extra_fields or {}),
            },
            updated_at=extracted_at,
        )
