from dataclasses import dataclass
from datetime import UTC, datetime
import re

from app.schemas.documents import (
    BoundingBox,
    DocumentFields,
    DocumentMetadata,
    ExtractedField,
    InvoiceLineItem,
    OcrResult,
    OcrStatus,
    ParserResult,
    ParserSource,
    ParserStatus,
)


@dataclass(frozen=True)
class SourceLine:
    text: str
    page_number: int | None = None
    bbox: BoundingBox | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class ParsedAmount:
    value: float
    currency: str | None


class DeterministicInvoiceParser:
    parser_source: ParserSource = "deterministic_invoice"
    schema_version = "invoice_fields_v1"

    vendor_patterns = [
        re.compile(r"\b(?:vendor|supplier|seller)\s*[:：]\s*(?P<value>.+)", re.IGNORECASE),
        re.compile(r"(?:供應商|供应商|廠商|厂商|賣方|卖方)\s*[:：]\s*(?P<value>.+)"),
    ]
    invoice_number_patterns = [
        re.compile(
            r"\b(?:invoice\s*(?:number|no\.?|#)|inv\s*(?:no\.?|#))\s*[:：#-]?\s*(?P<value>[A-Za-z0-9][A-Za-z0-9._/-]{2,})",
            re.IGNORECASE,
        ),
        re.compile(r"(?:發票號碼|发票号码|發票號|发票号)\s*[:：]?\s*(?P<value>[A-Za-z0-9][A-Za-z0-9._/-]{2,})"),
    ]
    issue_date_patterns = [
        re.compile(
            r"\b(?:issue\s*date|invoice\s*date|date)\s*[:：]\s*(?P<value>\d{4}[-/年]\d{1,2}[-/月]\d{1,2}(?:日)?)",
            re.IGNORECASE,
        ),
        re.compile(r"(?:開立日期|开立日期|發票日期|发票日期|日期)\s*[:：]\s*(?P<value>\d{4}[-/年]\d{1,2}[-/月]\d{1,2}(?:日)?)"),
    ]
    currency_pattern = re.compile(r"\b(?:USD|TWD|NTD|EUR|JPY|CNY|RMB)\b|NT\$|US\$|\$", re.IGNORECASE)

    def parse(self, document: DocumentMetadata, parsed_at: datetime | None = None) -> ParserResult:
        parsed_at = parsed_at or datetime.now(UTC)
        source_ocr_status = document.ocr.status

        if source_ocr_status != OcrStatus.COMPLETED:
            return self._failed_result(
                document,
                parsed_at,
                fallback_reason="ocr_not_completed",
                error_message="Document OCR must be completed before invoice parsing.",
            )

        source_lines = self._source_lines(document.ocr)
        if not source_lines:
            return self._failed_result(
                document,
                parsed_at,
                fallback_reason="empty_ocr_text",
                error_message="Document OCR text is empty.",
            )

        fields = DocumentFields(
            document_type=self._document_type_field(source_lines),
            vendor_name=self._labeled_text_field(source_lines, self.vendor_patterns, confidence=0.84),
            invoice_number=self._labeled_text_field(source_lines, self.invoice_number_patterns, confidence=0.88),
            issue_date=self._issue_date_field(source_lines),
            total_amount=self._amount_field(source_lines, self._is_total_line, confidence=0.86),
            tax_amount=self._amount_field(source_lines, self._is_tax_line, confidence=0.8),
            line_items=self._line_items(source_lines),
        )
        fields.currency = self._currency_field(source_lines, fields.total_amount, fields.tax_amount)

        missing_fields = self._missing_field_names(fields)
        trace_metadata = {
            "input": "ocr_lines" if document.ocr.lines else "ocr_text",
            "parser_mode": "deterministic",
            "line_count": str(len(source_lines)),
            "line_items_count": str(len(fields.line_items)),
            "missing_fields": ",".join(missing_fields),
        }

        return ParserResult(
            document_id=document.document_id,
            status=ParserStatus.PARSED,
            parser_source=self.parser_source,
            schema_version=self.schema_version,
            fields=fields,
            fallback_reason="missing_fields" if missing_fields else None,
            source_ocr_status=source_ocr_status,
            source_ocr_updated_at=document.ocr.updated_at,
            updated_at=parsed_at,
            trace_metadata=trace_metadata,
        )

    def _failed_result(
        self,
        document: DocumentMetadata,
        parsed_at: datetime,
        fallback_reason: str,
        error_message: str,
    ) -> ParserResult:
        return ParserResult(
            document_id=document.document_id,
            status=ParserStatus.FAILED,
            parser_source=self.parser_source,
            schema_version=self.schema_version,
            fields=DocumentFields(),
            fallback_reason=fallback_reason,
            error_message=error_message,
            source_ocr_status=document.ocr.status,
            source_ocr_updated_at=document.ocr.updated_at,
            updated_at=parsed_at,
            trace_metadata={
                "input": "ocr_lines" if document.ocr.lines else "ocr_text",
                "parser_mode": "deterministic",
                "missing_fields": "document_type,vendor_name,invoice_number,issue_date,total_amount,tax_amount,currency,line_items",
            },
        )

    def _source_lines(self, ocr_result: OcrResult) -> list[SourceLine]:
        if ocr_result.lines:
            return [
                SourceLine(
                    text=line.text.strip(),
                    page_number=line.page_number,
                    bbox=line.bbox,
                    confidence=line.confidence,
                )
                for line in ocr_result.lines
                if line.text.strip()
            ]

        return [
            SourceLine(text=line.strip())
            for line in ocr_result.text.splitlines()
            if line.strip()
        ]

    def _document_type_field(self, source_lines: list[SourceLine]) -> ExtractedField:
        for line in source_lines:
            if re.search(r"\binvoice\b|發票|发票", line.text, re.IGNORECASE):
                return self._field("invoice", line, confidence=0.9)

        return ExtractedField(
            value="invoice",
            confidence=0.5,
            parser_source=self.parser_source,
            fallback_reason="parser_default_invoice",
        )

    def _labeled_text_field(
        self,
        source_lines: list[SourceLine],
        patterns: list[re.Pattern[str]],
        confidence: float,
    ) -> ExtractedField:
        for line in source_lines:
            for pattern in patterns:
                match = pattern.search(line.text)
                if match:
                    value = self._clean_text_value(match.group("value"))
                    if value:
                        return self._field(value, line, confidence=confidence)

        return self._missing_field()

    def _issue_date_field(self, source_lines: list[SourceLine]) -> ExtractedField:
        for line in source_lines:
            if re.search(r"\b(?:due\s*date|payment\s*due)\b|到期日|付款期限", line.text, re.IGNORECASE):
                continue

            for pattern in self.issue_date_patterns:
                match = pattern.search(line.text)
                if not match:
                    continue

                value = self._normalize_date(match.group("value"))
                if value:
                    return self._field(value, line, confidence=0.86)

                return self._field(
                    None,
                    line,
                    confidence=None,
                    fallback_reason="date_normalization_failed",
                )

        return self._missing_field()

    def _amount_field(
        self,
        source_lines: list[SourceLine],
        label_predicate,
        confidence: float,
    ) -> ExtractedField:
        for line in source_lines:
            if not label_predicate(line.text):
                continue

            parsed_amount = self._extract_amount(line.text)
            if parsed_amount is None:
                return self._field(
                    None,
                    line,
                    confidence=None,
                    fallback_reason="amount_normalization_failed",
                )

            return self._field(parsed_amount.value, line, confidence=confidence)

        return self._missing_field()

    def _currency_field(
        self,
        source_lines: list[SourceLine],
        total_amount: ExtractedField,
        tax_amount: ExtractedField,
    ) -> ExtractedField:
        for field in (total_amount, tax_amount):
            if field.source_text:
                parsed_amount = self._extract_amount(field.source_text)
                if parsed_amount and parsed_amount.currency:
                    return ExtractedField(
                        value=parsed_amount.currency,
                        confidence=field.confidence,
                        source_text=field.source_text,
                        source_page=field.source_page,
                        source_bbox=field.source_bbox,
                        parser_source=self.parser_source,
                    )

        for line in source_lines:
            match = self.currency_pattern.search(line.text)
            if match:
                currency = self._normalize_currency(match.group(0))
                if currency:
                    return self._field(currency, line, confidence=0.78)

        return self._missing_field()

    def _line_items(self, source_lines: list[SourceLine]) -> list[InvoiceLineItem]:
        line_items: list[InvoiceLineItem] = []
        in_line_items = False

        for line in source_lines:
            if re.search(r"\bline\s*items?\b|品項|项目|明細|明细", line.text, re.IGNORECASE):
                in_line_items = True
                continue

            if not in_line_items:
                continue

            if re.search(r"\bnotes?\b|備註|备注|subtotal|tax|amount\s*due|total", line.text, re.IGNORECASE):
                break

            clean_text = re.sub(r"^\s*[-*•]\s*", "", line.text).strip()
            if not clean_text:
                continue

            line_items.append(self._line_item(clean_text, line))

        return line_items

    def _line_item(self, clean_text: str, line: SourceLine) -> InvoiceLineItem:
        match = re.match(
            r"(?P<quantity>\d+(?:\.\d+)?)\s+(?P<description>.+?)\s+(?:at|@|x)\s+.+",
            clean_text,
            re.IGNORECASE,
        )
        parsed_amount = self._extract_amount(clean_text)

        if match:
            quantity_value = self._number_value(match.group("quantity"))
            description = self._clean_text_value(match.group("description"))
            return InvoiceLineItem(
                description=self._field(description, line, confidence=0.74),
                quantity=self._field(quantity_value, line, confidence=0.74),
                unit_price=self._field(parsed_amount.value, line, confidence=0.74)
                if parsed_amount
                else self._missing_field("amount_normalization_failed"),
                amount=self._missing_field(),
            )

        return InvoiceLineItem(
            description=self._field(clean_text, line, confidence=0.68),
            quantity=self._missing_field(),
            unit_price=self._missing_field(),
            amount=self._missing_field(),
        )

    def _is_total_line(self, text: str) -> bool:
        lower_text = text.lower()
        if "subtotal" in lower_text:
            return False

        return bool(
            re.search(
                r"\b(?:amount\s*due|total\s*amount|grand\s*total|total)\b|總計|总计|總金額|总金额|應付金額|应付金额",
                text,
                re.IGNORECASE,
            )
        )

    def _is_tax_line(self, text: str) -> bool:
        return bool(re.search(r"\b(?:tax|vat)\b|稅額|税额|營業稅|营业税", text, re.IGNORECASE))

    def _extract_amount(self, text: str) -> ParsedAmount | None:
        currency_token = r"(?:USD|TWD|NTD|EUR|JPY|CNY|RMB|NT\$|US\$|\$)"
        patterns = [
            re.compile(
                rf"(?P<currency>{currency_token})\s*(?P<amount>\d[\d,]*(?:\.\d+)?)",
                re.IGNORECASE,
            ),
            re.compile(
                rf"(?P<amount>\d[\d,]*(?:\.\d+)?)\s*(?P<currency>{currency_token})",
                re.IGNORECASE,
            ),
            re.compile(r"(?P<amount>\d[\d,]*(?:\.\d+)?)"),
        ]

        for pattern in patterns:
            match = pattern.search(text)
            if not match:
                continue

            amount = self._number_value(match.group("amount"))
            if not isinstance(amount, (int, float)):
                continue

            currency = None
            if "currency" in match.groupdict() and match.group("currency"):
                currency = self._normalize_currency(match.group("currency"))

            return ParsedAmount(value=float(amount), currency=currency)

        return None

    def _normalize_currency(self, value: str) -> str | None:
        normalized = value.strip().upper()
        if normalized in {"NT$", "NTD", "TWD"}:
            return "TWD"
        if normalized in {"US$", "$", "USD"}:
            return "USD"
        if normalized == "RMB":
            return "CNY"
        if normalized in {"EUR", "JPY", "CNY"}:
            return normalized

        return None

    def _normalize_date(self, value: str) -> str | None:
        match = re.search(r"(?P<year>\d{4})[-/年](?P<month>\d{1,2})[-/月](?P<day>\d{1,2})", value)
        if not match:
            return None

        return f"{int(match.group('year')):04d}-{int(match.group('month')):02d}-{int(match.group('day')):02d}"

    def _number_value(self, value: str) -> int | float | None:
        try:
            number = float(value.replace(",", ""))
        except ValueError:
            return None

        if number.is_integer():
            return int(number)

        return number

    def _field(
        self,
        value: str | int | float | bool | None,
        source_line: SourceLine,
        confidence: float | None,
        fallback_reason: str | None = None,
    ) -> ExtractedField:
        if confidence is not None and source_line.confidence is not None:
            confidence = min(confidence, source_line.confidence)

        return ExtractedField(
            value=value,
            confidence=confidence,
            source_text=source_line.text,
            source_page=source_line.page_number,
            source_bbox=source_line.bbox,
            parser_source=self.parser_source,
            fallback_reason=fallback_reason,
        )

    def _missing_field(self, fallback_reason: str = "field_not_found") -> ExtractedField:
        return ExtractedField(parser_source=self.parser_source, fallback_reason=fallback_reason)

    def _clean_text_value(self, value: str) -> str:
        return value.strip().strip(" -")

    def _missing_field_names(self, fields: DocumentFields) -> list[str]:
        missing_fields = [
            field_name
            for field_name in [
                "document_type",
                "vendor_name",
                "invoice_number",
                "issue_date",
                "total_amount",
                "tax_amount",
                "currency",
            ]
            if getattr(fields, field_name).value is None
        ]
        if not fields.line_items:
            missing_fields.append("line_items")

        return missing_fields
