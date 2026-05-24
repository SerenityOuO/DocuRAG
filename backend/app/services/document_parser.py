from dataclasses import dataclass
from datetime import UTC, datetime
import base64
import json
import re

import httpx

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
from app.services.vlm_input import VlmInputDescriptor, VlmInputResolver


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


class VlmProviderError(Exception):
    def __init__(self, fallback_reason: str, message: str) -> None:
        super().__init__(message)
        self.fallback_reason = fallback_reason


class DisabledVlmProvider:
    provider_name = "disabled"
    model_name = "disabled"

    def extract_invoice_fields(self, _descriptor: VlmInputDescriptor) -> dict:
        raise VlmProviderError("vlm_provider_unavailable", "VLM provider is disabled.")


class FakeVlmProvider:
    provider_name = "fake"
    model_name = "fake-vlm-invoice"

    def extract_invoice_fields(self, _descriptor: VlmInputDescriptor) -> dict:
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
                    "description": "6 ergonomic chair kits",
                    "quantity": 6,
                    "unit_price": 149.0,
                    "amount": 894.0,
                }
            ],
            "confidence": 0.82,
        }


class OllamaVlmProvider:
    provider_name = "ollama"

    def __init__(self, base_url: str, model_name: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def extract_invoice_fields(self, descriptor: VlmInputDescriptor) -> dict:
        if descriptor.file_path is None:
            raise VlmProviderError("missing_file", "VLM input file was unavailable.")

        prompt = (
            "Extract invoice fields from this document image. Return only one JSON object with "
            "document_type, vendor_name, invoice_number, issue_date, total_amount, tax_amount, "
            "currency, line_items, and confidence."
        )
        image_base64 = base64.b64encode(descriptor.file_path.read_bytes()).decode("ascii")

        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise VlmProviderError("vlm_timeout", "VLM provider request timed out.") from exc
        except httpx.HTTPError as exc:
            raise VlmProviderError("vlm_provider_unavailable", "VLM provider request failed.") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise VlmProviderError("vlm_invalid_response", "VLM provider returned non-JSON response.") from exc

        raw_content = payload.get("response", payload)
        if isinstance(raw_content, str):
            try:
                parsed_content = json.loads(raw_content)
            except ValueError as exc:
                raise VlmProviderError("vlm_invalid_response", "VLM provider response was not a JSON object.") from exc
        else:
            parsed_content = raw_content

        if not isinstance(parsed_content, dict):
            raise VlmProviderError("vlm_invalid_response", "VLM provider response was not a JSON object.")

        return parsed_content


def create_vlm_provider(
    provider_name: str | None,
    base_url: str,
    model_name: str,
    timeout_seconds: float,
):
    normalized_provider = (provider_name or "").strip().lower()
    if not normalized_provider:
        return DisabledVlmProvider()

    if normalized_provider == "ollama":
        return OllamaVlmProvider(base_url, model_name, timeout_seconds)

    if normalized_provider == "fake":
        return FakeVlmProvider()

    return DisabledVlmProvider()


class VlmInvoiceParser:
    parser_source: ParserSource = "vlm_invoice"
    schema_version = "invoice_fields_v1"

    required_fields = ["document_type", "vendor_name", "invoice_number", "issue_date", "total_amount", "currency"]

    def __init__(
        self,
        input_resolver: VlmInputResolver,
        provider,
        min_confidence: float = 0.5,
        fallback_parser: "DeterministicInvoiceParser | None" = None,
    ) -> None:
        self.input_resolver = input_resolver
        self.provider = provider
        self.min_confidence = min_confidence
        self.fallback_parser = fallback_parser or DeterministicInvoiceParser()

    def parse(self, document: DocumentMetadata, parsed_at: datetime | None = None) -> ParserResult:
        parsed_at = parsed_at or datetime.now(UTC)

        if document.ocr.status != OcrStatus.COMPLETED:
            result = self.fallback_parser.parse(document, parsed_at=parsed_at)
            trace_metadata = dict(result.trace_metadata)
            trace_metadata.update(
                {
                    "parser_route": "vlm_first",
                    "fallback_chain": "deterministic_invoice",
                    "fallback_reason": result.fallback_reason or "ocr_not_completed",
                    "source_input_type": trace_metadata.get("input", "ocr_text"),
                }
            )
            return ParserResult(
                document_id=result.document_id,
                status=result.status,
                parser_source=result.parser_source,
                schema_version=result.schema_version,
                fields=result.fields,
                fallback_reason=result.fallback_reason,
                error_message=result.error_message,
                source_ocr_status=result.source_ocr_status,
                source_ocr_updated_at=result.source_ocr_updated_at,
                updated_at=result.updated_at,
                trace_metadata=trace_metadata,
            )

        descriptor = self.input_resolver.resolve(document)
        if not descriptor.is_supported:
            return self._fallback(document, parsed_at, descriptor.fallback_reason or "vlm_input_unavailable", descriptor)

        try:
            payload = self.provider.extract_invoice_fields(descriptor)
            fields, confidence = self._fields_from_payload(payload)
        except VlmProviderError as exc:
            return self._fallback(document, parsed_at, exc.fallback_reason, descriptor)

        if confidence < self.min_confidence:
            return self._fallback(document, parsed_at, "vlm_low_confidence", descriptor)

        missing_fields = [
            field_name for field_name in self.required_fields if getattr(fields, field_name).value is None
        ]
        if missing_fields:
            return self._fallback(document, parsed_at, "vlm_missing_fields", descriptor)

        return ParserResult(
            document_id=document.document_id,
            status=ParserStatus.PARSED,
            parser_source=self.parser_source,
            schema_version=self.schema_version,
            fields=fields,
            fallback_reason=None,
            source_ocr_status=document.ocr.status,
            source_ocr_updated_at=document.ocr.updated_at,
            updated_at=parsed_at,
            trace_metadata=self._trace_metadata(
                descriptor,
                fallback_chain="vlm_invoice",
                confidence=confidence,
            ),
        )

    def _fallback(
        self,
        document: DocumentMetadata,
        parsed_at: datetime,
        fallback_reason: str,
        descriptor: VlmInputDescriptor,
    ) -> ParserResult:
        result = self.fallback_parser.parse(document, parsed_at=parsed_at)
        trace_metadata = dict(result.trace_metadata)
        trace_metadata.update(
            self._trace_metadata(
                descriptor,
                fallback_chain="vlm_invoice -> deterministic_invoice",
                fallback_reason=fallback_reason,
            )
        )

        deterministic_fallback_reason = result.fallback_reason
        if deterministic_fallback_reason:
            trace_metadata["deterministic_fallback_reason"] = deterministic_fallback_reason

        return ParserResult(
            document_id=result.document_id,
            status=result.status,
            parser_source=result.parser_source,
            schema_version=result.schema_version,
            fields=result.fields,
            fallback_reason=fallback_reason,
            error_message=result.error_message,
            source_ocr_status=result.source_ocr_status,
            source_ocr_updated_at=result.source_ocr_updated_at,
            updated_at=result.updated_at,
            trace_metadata=trace_metadata,
        )

    def _trace_metadata(
        self,
        descriptor: VlmInputDescriptor,
        fallback_chain: str,
        fallback_reason: str | None = None,
        confidence: float | None = None,
    ) -> dict[str, str]:
        metadata = {
            "parser_route": "vlm_first",
            "vlm_provider": getattr(self.provider, "provider_name", "unknown"),
            "vlm_model": getattr(self.provider, "model_name", "unknown"),
            "source_input_type": "image" if descriptor.mime_type else "unavailable",
            "source_input": descriptor.input_source,
            "fallback_chain": fallback_chain,
        }
        if descriptor.mime_type:
            metadata["source_mime_type"] = descriptor.mime_type
        if fallback_reason:
            metadata["fallback_reason"] = fallback_reason
        if confidence is not None:
            metadata["confidence_summary"] = f"{confidence:.4f}"

        return metadata

    def _fields_from_payload(self, payload: dict) -> tuple[DocumentFields, float]:
        confidence = self._confidence(payload.get("confidence"))
        fields = DocumentFields(
            document_type=self._payload_field(payload, "document_type", confidence),
            vendor_name=self._payload_field(payload, "vendor_name", confidence),
            invoice_number=self._payload_field(payload, "invoice_number", confidence),
            issue_date=self._payload_field(payload, "issue_date", confidence),
            total_amount=self._payload_field(payload, "total_amount", confidence),
            tax_amount=self._payload_field(payload, "tax_amount", confidence, required=False),
            currency=self._payload_field(payload, "currency", confidence),
            line_items=self._line_items_from_payload(payload.get("line_items"), confidence),
        )
        return fields, confidence

    def _payload_field(
        self,
        payload: dict,
        field_name: str,
        confidence: float,
        required: bool = True,
    ) -> ExtractedField:
        value = payload.get(field_name)
        if value is None or value == "":
            return ExtractedField(
                parser_source=self.parser_source,
                fallback_reason="field_not_found" if required else None,
            )

        return ExtractedField(
            value=value,
            confidence=confidence,
            source_text=f"vlm:{field_name}",
            parser_source=self.parser_source,
        )

    def _line_items_from_payload(self, raw_items: object, confidence: float) -> list[InvoiceLineItem]:
        if not isinstance(raw_items, list):
            return []

        line_items: list[InvoiceLineItem] = []
        for raw_item in raw_items:
            if not isinstance(raw_item, dict):
                continue

            line_items.append(
                InvoiceLineItem(
                    description=self._payload_field(raw_item, "description", confidence, required=False),
                    quantity=self._payload_field(raw_item, "quantity", confidence, required=False),
                    unit_price=self._payload_field(raw_item, "unit_price", confidence, required=False),
                    amount=self._payload_field(raw_item, "amount", confidence, required=False),
                )
            )

        return line_items

    def _confidence(self, value: object) -> float:
        if not isinstance(value, (int, float)):
            raise VlmProviderError("vlm_invalid_response", "VLM response confidence must be numeric.")

        confidence = float(value)
        if confidence < 0 or confidence > 1:
            raise VlmProviderError("vlm_invalid_response", "VLM response confidence must be between 0 and 1.")

        return confidence


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
            "parser_route": "deterministic_only",
            "fallback_chain": "deterministic_invoice",
            "source_input_type": "ocr_lines" if document.ocr.lines else "ocr_text",
            "line_count": str(len(source_lines)),
            "line_items_count": str(len(fields.line_items)),
            "missing_fields": ",".join(missing_fields),
            "confidence_summary": self._confidence_summary(fields),
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
                "parser_route": "deterministic_only",
                "fallback_chain": "deterministic_invoice",
                "fallback_reason": fallback_reason,
                "source_input_type": "ocr_lines" if document.ocr.lines else "ocr_text",
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

    def _confidence_summary(self, fields: DocumentFields) -> str:
        confidences = [
            field.confidence
            for field in [
                fields.document_type,
                fields.vendor_name,
                fields.invoice_number,
                fields.issue_date,
                fields.total_amount,
                fields.tax_amount,
                fields.currency,
            ]
            if field.confidence is not None
        ]

        if not confidences:
            return "unavailable"

        return f"{sum(confidences) / len(confidences):.4f}"
