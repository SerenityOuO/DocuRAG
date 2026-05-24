from datetime import UTC, datetime
from pathlib import Path

from app.schemas.documents import DocumentMetadata, DocumentStatus
from app.services.vlm_input import VlmInputResolver


def _document(stored_filename: str, file_type: str = "png", content_type: str = "image/png") -> DocumentMetadata:
    return DocumentMetadata(
        document_id="doc-vlm-input-001",
        filename=f"sample.{file_type}",
        stored_filename=stored_filename,
        file_type=file_type,
        content_type=content_type,
        size=10,
        status=DocumentStatus.UPLOADED,
        created_at=datetime(2026, 5, 24, tzinfo=UTC),
    )


def test_vlm_input_resolver_returns_supported_image_descriptor(tmp_path: Path) -> None:
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    image_path = upload_dir / "doc-001-sample.png"
    image_path.write_bytes(b"\x89PNG\r\n")

    descriptor = VlmInputResolver(upload_dir).resolve(_document("doc-001-sample.png"))

    assert descriptor.is_supported is True
    assert descriptor.document_id == "doc-vlm-input-001"
    assert descriptor.file_path == image_path.resolve()
    assert descriptor.mime_type == "image/png"
    assert descriptor.input_source == "uploaded_file"
    assert descriptor.fallback_reason is None


def test_vlm_input_resolver_returns_missing_file_reason(tmp_path: Path) -> None:
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    descriptor = VlmInputResolver(upload_dir).resolve(_document("missing.jpg", file_type="jpg"))

    assert descriptor.is_supported is False
    assert descriptor.file_path is None
    assert descriptor.mime_type == "image/jpeg"
    assert descriptor.fallback_reason == "missing_file"


def test_vlm_input_resolver_rejects_unsupported_extension(tmp_path: Path) -> None:
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    text_path = upload_dir / "doc-001-sample.txt"
    text_path.write_text("not an image", encoding="utf-8")

    descriptor = VlmInputResolver(upload_dir).resolve(
        _document("doc-001-sample.txt", file_type="txt", content_type="text/plain")
    )

    assert descriptor.is_supported is False
    assert descriptor.file_path is None
    assert descriptor.mime_type is None
    assert descriptor.fallback_reason == "unsupported_file"


def test_vlm_input_resolver_rejects_unsafe_path(tmp_path: Path) -> None:
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    outside_path = tmp_path / "outside.png"
    outside_path.write_bytes(b"png")

    descriptor = VlmInputResolver(upload_dir).resolve(_document("../outside.png"))

    assert descriptor.is_supported is False
    assert descriptor.file_path is None
    assert descriptor.fallback_reason == "unsafe_path"
