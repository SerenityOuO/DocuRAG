from datetime import UTC, datetime
from pathlib import Path

from app.schemas.documents import (
    BoundingBox,
    DocumentMetadata,
    DocumentStatus,
    OcrResult,
    OcrStatus,
    OcrTextLine,
    ParserStatus,
)
from app.api.routes.documents import get_document_parser
from app.core.config import get_settings
from app.services.document_parser import (
    DeterministicInvoiceParser,
    FakeVlmProvider as RuntimeFakeVlmProvider,
    VlmInvoiceParser,
    VlmProviderError,
    create_vlm_provider,
)
from app.services.vlm_input import VlmInputResolver


class FakeVlmProvider:
    provider_name = "fake"
    model_name = "fake-vlm"

    def __init__(self, payload: dict | None = None, fallback_reason: str | None = None) -> None:
        self.payload = payload or {}
        self.fallback_reason = fallback_reason
        self.last_descriptor = None

    def extract_invoice_fields(self, descriptor):
        self.last_descriptor = descriptor
        if self.fallback_reason is not None:
            raise VlmProviderError(self.fallback_reason, "fake provider failure")

        return self.payload


def _document_with_ocr(
    text: str,
    lines: list[OcrTextLine] | None = None,
    ocr_status: OcrStatus = OcrStatus.COMPLETED,
) -> DocumentMetadata:
    return DocumentMetadata(
        document_id="doc-parser-001",
        filename="invoice.txt",
        stored_filename="doc-parser-001-invoice.txt",
        file_type="txt",
        content_type="text/plain",
        size=len(text.encode("utf-8")),
        status=DocumentStatus.READY if ocr_status == OcrStatus.COMPLETED else DocumentStatus.UPLOADED,
        created_at=datetime(2026, 5, 24, tzinfo=UTC),
        ocr=OcrResult(
            status=ocr_status,
            text=text,
            lines=lines or [],
            updated_at=datetime(2026, 5, 24, 1, 2, 3, tzinfo=UTC)
            if ocr_status == OcrStatus.COMPLETED
            else None,
        ),
    )


def _vlm_document(tmp_path: Path, invoice_text: str) -> tuple[DocumentMetadata, VlmInputResolver]:
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    (upload_dir / "doc-parser-001-invoice.png").write_bytes(b"\x89PNG\r\n")
    document = _document_with_ocr(invoice_text)
    document.stored_filename = "doc-parser-001-invoice.png"
    document.file_type = "png"
    document.content_type = "image/png"
    return document, VlmInputResolver(upload_dir)


def _complete_invoice_text() -> str:
    return "\n".join(
        [
            "Fictitious Demo SaaS Invoice",
            "Invoice number: ORN-2026-118",
            "Vendor: Orion Analytics Demo Software",
            "Issue date: 2026-06-01",
            "Tax: USD 288.00",
            "Amount due: USD 3,888.00",
            "Line items:",
            "- 12 analytics seats at USD 250.00 each",
        ]
    )


def _vlm_payload() -> dict:
    return {
        "document_type": "invoice",
        "vendor_name": "Aurora Office Supplies Demo LLC",
        "invoice_number": "AUR-2026-051",
        "issue_date": "2026-05-31",
        "total_amount": 1248.5,
        "tax_amount": 80.0,
        "currency": "USD",
        "line_items": [
            {
                "description": "Printer paper",
                "quantity": 5,
                "unit_price": 18.5,
                "amount": 92.5,
            }
        ],
        "confidence": 0.82,
    }


def _aurora_ocr_lines() -> list[OcrTextLine]:
    lines = [
        "Aurora Office Supplies Demo LLC Invoice",
        "Invoice number: AUR-2026-051",
        "Vendor: Aurora Office Supplies Demo LLC",
        "Issue date: 2026-05-31",
        "Tax: USD 80.00",
        "Amount due: USD 1,248.50",
        "Line items:",
        "Printer paper quantity 5 unit price USD 18.50 amount USD 92.50",
    ]
    return [
        OcrTextLine(
            text=line,
            page_number=1,
            bbox=BoundingBox(x_min=10, y_min=20 + index * 12, x_max=420, y_max=30 + index * 12),
            confidence=0.95,
        )
        for index, line in enumerate(lines)
    ]


def test_vlm_invoice_parser_returns_vlm_parser_result(tmp_path: Path) -> None:
    document, resolver = _vlm_document(tmp_path, _complete_invoice_text())
    parser = VlmInvoiceParser(resolver, FakeVlmProvider(_vlm_payload()))

    result = parser.parse(document)

    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "vlm_invoice"
    assert result.fields.invoice_number.value == "AUR-2026-051"
    assert result.fields.invoice_number.parser_source == "vlm_invoice"
    assert result.fields.invoice_number.confidence == 0.82
    assert result.fields.line_items[0].description.value == "Printer paper"
    assert result.trace_metadata["parser_route"] == "vlm_first"
    assert result.trace_metadata["fallback_chain"] == "vlm_invoice"
    assert result.trace_metadata["confidence_summary"] == "0.8200"
    assert result.trace_metadata["source_input_type"] == "image"


def test_vlm_invoice_parser_sends_image_and_ocr_context_and_maps_field_evidence(tmp_path: Path) -> None:
    ocr_lines = _aurora_ocr_lines()
    document, resolver = _vlm_document(tmp_path, "\n".join(line.text for line in ocr_lines))
    document.ocr.lines = ocr_lines
    provider = FakeVlmProvider(_vlm_payload())
    parser = VlmInvoiceParser(resolver, provider)

    result = parser.parse(document)

    assert provider.last_descriptor is not None
    assert provider.last_descriptor.file_path is not None
    assert provider.last_descriptor.mime_type == "image/png"
    assert len(provider.last_descriptor.ocr_context_lines) == len(ocr_lines)
    assert provider.last_descriptor.ocr_context_lines[1].text == "Invoice number: AUR-2026-051"
    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "vlm_invoice"
    assert result.fields.invoice_number.value == "AUR-2026-051"
    assert result.fields.invoice_number.source_text == "Invoice number: AUR-2026-051"
    assert result.fields.invoice_number.source_page == 1
    assert result.fields.invoice_number.source_bbox == BoundingBox(x_min=10, y_min=32, x_max=420, y_max=42)
    assert result.fields.invoice_number.fallback_reason is None
    assert result.fields.line_items[0].amount.source_text == (
        "Printer paper quantity 5 unit price USD 18.50 amount USD 92.50"
    )
    assert result.trace_metadata["ocr_context_state"] == "available"
    assert result.trace_metadata["ocr_context_line_count"] == str(len(ocr_lines))
    assert result.trace_metadata["field_evidence_state"] == "matched"
    assert result.trace_metadata["field_evidence_unmatched_count"] == "0"


def test_vlm_invoice_parser_marks_unmatched_field_evidence_without_fake_bbox(tmp_path: Path) -> None:
    ocr_lines = [
        OcrTextLine(
            text="Unrelated OCR line",
            page_number=1,
            bbox=BoundingBox(x_min=1, y_min=2, x_max=3, y_max=4),
            confidence=0.9,
        )
    ]
    document, resolver = _vlm_document(tmp_path, "\n".join(line.text for line in ocr_lines))
    document.ocr.lines = ocr_lines
    parser = VlmInvoiceParser(resolver, FakeVlmProvider(_vlm_payload()))

    result = parser.parse(document)

    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "vlm_invoice"
    assert result.fields.invoice_number.value == "AUR-2026-051"
    assert result.fields.invoice_number.source_text is None
    assert result.fields.invoice_number.source_page is None
    assert result.fields.invoice_number.source_bbox is None
    assert result.fields.invoice_number.fallback_reason == "evidence_unmatched"
    assert result.trace_metadata["field_evidence_state"] == "unmatched"
    assert "invoice_number" in result.trace_metadata["field_evidence_unmatched_fields"]


def test_runtime_fake_vlm_provider_returns_demo_invoice_payload(tmp_path: Path) -> None:
    document, resolver = _vlm_document(tmp_path, _complete_invoice_text())
    parser = VlmInvoiceParser(
        resolver,
        create_vlm_provider("fake", "http://127.0.0.1:11434", "ignored", 30),
    )

    result = parser.parse(document)

    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "vlm_invoice"
    assert result.fields.invoice_number.value == "AUR-2026-051"
    assert result.fields.invoice_number.parser_source == "vlm_invoice"
    assert result.trace_metadata["vlm_provider"] == "fake"
    assert result.trace_metadata["vlm_model"] == RuntimeFakeVlmProvider.model_name


def test_vlm_invoice_parser_falls_back_when_provider_is_unavailable(tmp_path: Path) -> None:
    document, resolver = _vlm_document(tmp_path, _complete_invoice_text())
    parser = VlmInvoiceParser(resolver, FakeVlmProvider(fallback_reason="vlm_provider_unavailable"))

    result = parser.parse(document)

    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "deterministic_invoice"
    assert result.fields.invoice_number.value == "ORN-2026-118"
    assert result.trace_metadata["parser_route"] == "vlm_first"
    assert result.trace_metadata["fallback_chain"] == "vlm_invoice -> deterministic_invoice"
    assert result.trace_metadata["fallback_reason"] == "vlm_provider_unavailable"


def test_vlm_invoice_parser_falls_back_on_timeout_or_provider_failure(tmp_path: Path) -> None:
    document, resolver = _vlm_document(tmp_path, _complete_invoice_text())
    parser = VlmInvoiceParser(resolver, FakeVlmProvider(fallback_reason="vlm_timeout"))

    result = parser.parse(document)

    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "deterministic_invoice"
    assert result.trace_metadata["fallback_reason"] == "vlm_timeout"


def test_vlm_invoice_parser_falls_back_on_invalid_json_shape(tmp_path: Path) -> None:
    document, resolver = _vlm_document(tmp_path, _complete_invoice_text())
    parser = VlmInvoiceParser(resolver, FakeVlmProvider({"confidence": "high"}))

    result = parser.parse(document)

    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "deterministic_invoice"
    assert result.trace_metadata["fallback_reason"] == "vlm_invalid_response"


def test_vlm_invoice_parser_falls_back_on_missing_fields(tmp_path: Path) -> None:
    document, resolver = _vlm_document(tmp_path, _complete_invoice_text())
    payload = _vlm_payload()
    payload.pop("invoice_number")
    parser = VlmInvoiceParser(resolver, FakeVlmProvider(payload))

    result = parser.parse(document)

    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "deterministic_invoice"
    assert result.fields.invoice_number.value == "ORN-2026-118"
    assert result.trace_metadata["fallback_reason"] == "vlm_missing_fields"


def test_document_parser_dependency_respects_explicit_deterministic_override(monkeypatch) -> None:
    monkeypatch.setenv("DOCURAG_PARSER_SOURCE", "deterministic_invoice")
    get_settings.cache_clear()

    try:
        parser = get_document_parser()

        assert isinstance(parser, DeterministicInvoiceParser)
        result = parser.parse(_document_with_ocr(_complete_invoice_text()))
        assert result.trace_metadata["parser_route"] == "deterministic_only"
        assert result.trace_metadata["fallback_chain"] == "deterministic_invoice"
    finally:
        monkeypatch.delenv("DOCURAG_PARSER_SOURCE", raising=False)
        get_settings.cache_clear()


def test_deterministic_invoice_parser_extracts_sample_invoice_fields() -> None:
    invoice_text = "\n".join(
        [
            "Fictitious Demo SaaS Invoice",
            "Invoice number: ORN-2026-118",
            "Vendor: Orion Analytics Demo Software",
            "Issue date: 2026-06-01",
            "Subtotal: USD 3,600.00",
            "Tax: USD 288.00",
            "Amount due: USD 3,888.00",
            "Line items:",
            "- 12 analytics seats at USD 250.00 each",
            "- 1 onboarding workshop at USD 600.00",
        ]
    )
    lines = [
        OcrTextLine(
            text=line,
            page_number=1,
            bbox=BoundingBox(x_min=10, y_min=20 + index * 12, x_max=260, y_max=30 + index * 12),
            confidence=0.96,
        )
        for index, line in enumerate(invoice_text.splitlines())
    ]
    parser = DeterministicInvoiceParser()

    result = parser.parse(_document_with_ocr(invoice_text, lines))

    assert result.status == ParserStatus.PARSED
    assert result.parser_source == "deterministic_invoice"
    assert result.schema_version == "invoice_fields_v1"
    assert result.fallback_reason is None
    assert result.source_ocr_status == OcrStatus.COMPLETED
    assert result.fields.document_type.value == "invoice"
    assert result.fields.vendor_name.value == "Orion Analytics Demo Software"
    assert result.fields.invoice_number.value == "ORN-2026-118"
    assert result.fields.invoice_number.source_text == "Invoice number: ORN-2026-118"
    assert result.fields.invoice_number.source_page == 1
    assert result.fields.invoice_number.source_bbox == BoundingBox(x_min=10, y_min=32, x_max=260, y_max=42)
    assert result.fields.invoice_number.confidence == 0.88
    assert result.fields.issue_date.value == "2026-06-01"
    assert result.fields.total_amount.value == 3888.0
    assert result.fields.tax_amount.value == 288.0
    assert result.fields.currency.value == "USD"
    assert result.fields.line_items[0].description.value == "analytics seats"
    assert result.fields.line_items[0].quantity.value == 12
    assert result.fields.line_items[0].unit_price.value == 250.0
    assert result.fields.line_items[0].amount.value is None
    assert result.fields.line_items[0].amount.fallback_reason == "field_not_found"
    assert result.trace_metadata["input"] == "ocr_lines"
    assert result.trace_metadata["line_items_count"] == "2"
    assert result.trace_metadata["parser_route"] == "deterministic_only"
    assert result.trace_metadata["fallback_chain"] == "deterministic_invoice"
    assert result.trace_metadata["confidence_summary"] != "unavailable"


def test_deterministic_invoice_parser_marks_missing_fields_without_fake_values() -> None:
    parser = DeterministicInvoiceParser()
    text = "\n".join(
        [
            "Invoice number: INV-2026-001",
            "Amount due: USD 10.00",
        ]
    )

    result = parser.parse(_document_with_ocr(text))

    assert result.status == ParserStatus.PARSED
    assert result.fallback_reason == "missing_fields"
    assert result.fields.invoice_number.value == "INV-2026-001"
    assert result.fields.total_amount.value == 10.0
    assert result.fields.vendor_name.value is None
    assert result.fields.vendor_name.fallback_reason == "field_not_found"
    assert result.fields.issue_date.value is None
    assert result.fields.issue_date.fallback_reason == "field_not_found"
    assert result.fields.tax_amount.value is None
    assert result.fields.tax_amount.fallback_reason == "field_not_found"
    assert "vendor_name" in result.trace_metadata["missing_fields"]
    assert "line_items" in result.trace_metadata["missing_fields"]


def test_deterministic_invoice_parser_handles_chinese_labels_and_twd_amounts() -> None:
    parser = DeterministicInvoiceParser()
    text = "\n".join(
        [
            "DocuRAG 繁中 OCR 測試發票",
            "發票號碼：OCR-2026-009",
            "供應商：星河科技股份有限公司",
            "日期：2026/05/24",
            "稅額：NTD 600",
            "總計 : NT$ 12,345",
        ]
    )

    result = parser.parse(_document_with_ocr(text))

    assert result.status == ParserStatus.PARSED
    assert result.fields.document_type.value == "invoice"
    assert result.fields.invoice_number.value == "OCR-2026-009"
    assert result.fields.vendor_name.value == "星河科技股份有限公司"
    assert result.fields.issue_date.value == "2026-05-24"
    assert result.fields.tax_amount.value == 600.0
    assert result.fields.total_amount.value == 12345.0
    assert result.fields.currency.value == "TWD"


def test_deterministic_invoice_parser_fails_when_ocr_is_not_completed() -> None:
    parser = DeterministicInvoiceParser()
    document = _document_with_ocr("", ocr_status=OcrStatus.PENDING)

    result = parser.parse(document)

    assert result.status == ParserStatus.FAILED
    assert result.fallback_reason == "ocr_not_completed"
    assert result.error_message == "Document OCR must be completed before invoice parsing."
    assert result.source_ocr_status == OcrStatus.PENDING
