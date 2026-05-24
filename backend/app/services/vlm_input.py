from dataclasses import dataclass
from pathlib import Path

from app.schemas.documents import DocumentMetadata


SUPPORTED_IMAGE_MIME_TYPES = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
}


@dataclass(frozen=True)
class VlmInputDescriptor:
    document_id: str
    file_path: Path | None
    mime_type: str | None
    input_source: str
    fallback_reason: str | None = None

    @property
    def is_supported(self) -> bool:
        return self.fallback_reason is None and self.file_path is not None


class VlmInputResolver:
    def __init__(self, upload_dir: Path) -> None:
        self.upload_dir = upload_dir

    def resolve(self, document: DocumentMetadata) -> VlmInputDescriptor:
        upload_root = self.upload_dir.resolve()
        file_path = (upload_root / document.stored_filename).resolve()

        try:
            file_path.relative_to(upload_root)
        except ValueError:
            return self._failure(document, "unsafe_path")

        suffix = file_path.suffix.lower()
        mime_type = SUPPORTED_IMAGE_MIME_TYPES.get(suffix)
        if mime_type is None:
            return self._failure(document, "unsupported_file")

        if not file_path.is_file():
            return self._failure(document, "missing_file", mime_type=mime_type)

        try:
            with file_path.open("rb") as image_file:
                image_file.read(1)
        except OSError:
            return self._failure(document, "file_not_readable", mime_type=mime_type)

        return VlmInputDescriptor(
            document_id=document.document_id,
            file_path=file_path,
            mime_type=mime_type,
            input_source="uploaded_file",
        )

    def _failure(
        self,
        document: DocumentMetadata,
        fallback_reason: str,
        mime_type: str | None = None,
    ) -> VlmInputDescriptor:
        return VlmInputDescriptor(
            document_id=document.document_id,
            file_path=None,
            mime_type=mime_type,
            input_source="uploaded_file",
            fallback_reason=fallback_reason,
        )
