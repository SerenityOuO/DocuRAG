from datetime import UTC, datetime

from app.schemas.documents import (
    BoundingBox,
    DocumentMetadata,
    DocumentStatus,
    OcrResult,
    OcrStatus,
    OcrTextLine,
    ParserStatus,
)
from app.services.document_parser import DeterministicInvoiceParser


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
