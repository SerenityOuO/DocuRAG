from dataclasses import dataclass
from pathlib import Path

from app.schemas.documents import BoundingBox, DocumentMetadata, OcrResult


SUPPORTED_IMAGE_MIME_TYPES = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
}


@dataclass(frozen=True)
class VlmOcrContextLine:
    text: str
    page_number: int | None = None
    bbox: BoundingBox | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class VlmInputDescriptor:
    document_id: str
    file_path: Path | None
    mime_type: str | None
    input_source: str
    fallback_reason: str | None = None
    ocr_context_lines: tuple[VlmOcrContextLine, ...] = ()

    @property
    def is_supported(self) -> bool:
        return self.fallback_reason is None and self.file_path is not None


class VlmInputResolver:
    max_ocr_context_lines = 30

    def __init__(self, upload_dir: Path) -> None:
        self.upload_dir = upload_dir

    def resolve(self, document: DocumentMetadata) -> VlmInputDescriptor:
        ocr_context_lines = self._ocr_context_lines(document.ocr)
        upload_root = self.upload_dir.resolve()
        file_path = (upload_root / document.stored_filename).resolve()

        try:
            file_path.relative_to(upload_root)
        except ValueError:
            return self._failure(document, "unsafe_path", ocr_context_lines=ocr_context_lines)

        suffix = file_path.suffix.lower()
        mime_type = SUPPORTED_IMAGE_MIME_TYPES.get(suffix)
        if mime_type is None:
            return self._failure(document, "unsupported_file", ocr_context_lines=ocr_context_lines)

        if not file_path.is_file():
            return self._failure(document, "missing_file", mime_type=mime_type, ocr_context_lines=ocr_context_lines)

        try:
            with file_path.open("rb") as image_file:
                image_file.read(1)
        except OSError:
            return self._failure(document, "file_not_readable", mime_type=mime_type, ocr_context_lines=ocr_context_lines)

        return VlmInputDescriptor(
            document_id=document.document_id,
            file_path=file_path,
            mime_type=mime_type,
            input_source="uploaded_file",
            ocr_context_lines=ocr_context_lines,
        )

    def _failure(
        self,
        document: DocumentMetadata,
        fallback_reason: str,
        mime_type: str | None = None,
        ocr_context_lines: tuple[VlmOcrContextLine, ...] = (),
    ) -> VlmInputDescriptor:
        return VlmInputDescriptor(
            document_id=document.document_id,
            file_path=None,
            mime_type=mime_type,
            input_source="uploaded_file",
            fallback_reason=fallback_reason,
            ocr_context_lines=ocr_context_lines,
        )

    def _ocr_context_lines(self, ocr_result: OcrResult) -> tuple[VlmOcrContextLine, ...]:
        context_lines: list[VlmOcrContextLine] = []

        if ocr_result.lines:
            for line in ocr_result.lines:
                clean_text = line.text.strip()
                if not clean_text:
                    continue

                context_lines.append(
                    VlmOcrContextLine(
                        text=clean_text,
                        page_number=line.page_number,
                        bbox=line.bbox,
                        confidence=line.confidence,
                    )
                )
                if len(context_lines) >= self.max_ocr_context_lines:
                    break

            return tuple(context_lines)

        for line in ocr_result.text.splitlines():
            clean_text = line.strip()
            if not clean_text:
                continue

            context_lines.append(VlmOcrContextLine(text=clean_text))
            if len(context_lines) >= self.max_ocr_context_lines:
                break

        return tuple(context_lines)
