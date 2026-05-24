from datetime import UTC, datetime
import json
from pathlib import Path

from app.schemas.agent import AgentToolStatus
from app.schemas.documents import (
    DocumentChunk,
    DocumentFields,
    DocumentMetadata,
    DocumentStatus,
    ExtractedField,
    InvoiceLineItem,
    ParserResult,
    ParserStatus,
)
from app.schemas.rag import RagCitation
from app.services.agent_tools import AgentToolService
from app.services.document_storage import DocumentStorage


def _write_documents(storage: DocumentStorage, documents: list[DocumentMetadata]) -> None:
    storage.data_dir.mkdir(parents=True, exist_ok=True)
    storage.upload_dir.mkdir(parents=True, exist_ok=True)
    storage.metadata_path.write_text(
        json.dumps([document.model_dump(mode="json") for document in documents], ensure_ascii=False),
        encoding="utf-8",
    )


def _invoice_fields() -> DocumentFields:
    return DocumentFields(
        document_type=ExtractedField(value="invoice", confidence=1.0),
        vendor_name=ExtractedField(value="Aurora Office Supplies Demo LLC", confidence=0.86),
        invoice_number=ExtractedField(value="AUR-2026-051", confidence=0.88),
        issue_date=ExtractedField(value="2026-05-31", confidence=0.84),
        total_amount=ExtractedField(value=1248.5, confidence=0.9),
        tax_amount=ExtractedField(value=80.0, confidence=0.86),
        currency=ExtractedField(value="USD", confidence=0.82),
        line_items=[
            InvoiceLineItem(
                description=ExtractedField(value="ergonomic chair kits"),
                quantity=ExtractedField(value=6),
                unit_price=ExtractedField(value=149.0),
                amount=ExtractedField(value=894.0),
            )
        ],
    )


def _parser_result(document_id: str = "doc-agent-001") -> ParserResult:
    return ParserResult(
        document_id=document_id,
        status=ParserStatus.PARSED,
        fields=_invoice_fields(),
        updated_at=datetime(2026, 5, 24, tzinfo=UTC),
        trace_metadata={"parser_mode": "deterministic"},
    )


def _document(
    document_id: str = "doc-agent-001",
    parser_result: ParserResult | None = None,
    chunks: list[DocumentChunk] | None = None,
) -> DocumentMetadata:
    return DocumentMetadata(
        document_id=document_id,
        filename="mock-invoice-aurora.txt",
        stored_filename=f"{document_id}-mock-invoice-aurora.txt",
        file_type="txt",
        content_type="text/plain",
        size=100,
        status=DocumentStatus.READY,
        created_at=datetime(2026, 5, 24, tzinfo=UTC),
        parser_result=parser_result,
        chunks=chunks or [],
    )


def test_get_document_fields_returns_saved_parser_result(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    parser_result = _parser_result()
    _write_documents(storage, [_document(parser_result=parser_result)])

    result = AgentToolService(storage).get_document_fields("doc-agent-001")

    assert result.status == AgentToolStatus.COMPLETED
    assert result.tool_name == "get_document_fields"
    assert result.output["fields"]["invoice_number"]["value"] == "AUR-2026-051"
    assert result.output_summary == (
        "invoice_number=AUR-2026-051; vendor=Aurora Office Supplies Demo LLC; total=1248.5 USD"
    )
    assert result.observation.message == "Parser result was available."
    assert result.observation.missing_fields == []
    assert result.trace_metadata["allowlisted"] == "true"
    assert result.trace_metadata["read_only"] == "true"
    assert result.trace_metadata["tool_source"] == "local_metadata"


def test_get_document_fields_returns_failure_when_parser_result_is_missing(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    _write_documents(storage, [_document(parser_result=None)])

    result = AgentToolService(storage).get_document_fields("doc-agent-001")

    assert result.status == AgentToolStatus.FAILED
    assert result.output["parser_status"] == "pending"
    assert result.observation.fallback_reason == "parser_result_missing"
    assert result.output_summary == "Parser result status is pending."


def test_search_documents_returns_keyword_results_and_citations(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    chunk = DocumentChunk(
        chunk_id="chunk-payment",
        document_id="doc-agent-001",
        text="Payment terms: Net 15",
        source="ocr_mock",
        created_at=datetime(2026, 5, 24, tzinfo=UTC),
        source_type="ocr_mock",
        metadata={"origin": "ocr_text", "provider": "ocr_mock"},
    )
    _write_documents(storage, [_document(chunks=[chunk])])

    result = AgentToolService(storage).search_documents(
        "payment terms",
        top_k=3,
        document_id="doc-agent-001",
    )

    assert result.status == AgentToolStatus.COMPLETED
    assert result.output_summary == "Retrieved 1 chunk(s)."
    assert result.output["retrieved_chunks"][0]["chunk_id"] == "chunk-payment"
    assert result.citations[0].chunk_id == "chunk-payment"
    assert result.citations[0].trace_metadata == {
        "source": "ocr_mock",
        "origin": "ocr_text",
        "provider": "ocr_mock",
    }
    assert result.trace_metadata["rag_provider"] == "keyword"
    assert result.trace_metadata["retrieved_chunk_count"] == "1"


def test_search_documents_returns_failure_when_query_has_no_match(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    chunk = DocumentChunk(
        chunk_id="chunk-payment",
        document_id="doc-agent-001",
        text="Payment terms: Net 15",
        source="ocr_mock",
        created_at=datetime(2026, 5, 24, tzinfo=UTC),
    )
    _write_documents(storage, [_document(chunks=[chunk])])

    result = AgentToolService(storage).search_documents("unsupported query", top_k=3)

    assert result.status == AgentToolStatus.FAILED
    assert result.observation.fallback_reason == "no_retrieved_chunks"
    assert result.output["retrieved_chunks"] == []
    assert result.trace_metadata["retrieved_chunk_count"] == "0"


def test_search_documents_returns_tool_error_failure(tmp_path: Path) -> None:
    class FailingRagProvider:
        name = "failing"

        def query(self, query: str, top_k: int, documents: list[DocumentMetadata]):
            raise RuntimeError("search backend failed")

    storage = DocumentStorage(tmp_path / "data")
    _write_documents(storage, [_document()])

    result = AgentToolService(storage, rag_provider=FailingRagProvider()).search_documents("invoice")

    assert result.status == AgentToolStatus.FAILED
    assert result.observation.fallback_reason == "tool_error"
    assert result.error_message == "search backend failed"
    assert result.trace_metadata["fallback_reason"] == "tool_error"


def test_summarize_invoice_fields_returns_deterministic_summary(tmp_path: Path) -> None:
    storage = DocumentStorage(tmp_path / "data")
    citation = RagCitation(
        document_id="doc-agent-001",
        filename="mock-invoice-aurora.txt",
        chunk_id="chunk-payment",
        trace_metadata={"source": "ocr_mock"},
    )

    result = AgentToolService(storage).summarize_invoice_fields(
        _parser_result(),
        citations=[citation],
    )

    assert result.status == AgentToolStatus.COMPLETED
    assert "Invoice AUR-2026-051 is from Aurora Office Supplies Demo LLC." in result.output_summary
    assert "Total amount: 1248.5 USD." in result.output_summary
    assert "Source chunks: chunk-payment." in result.output_summary
    assert result.output["summary"] == result.output_summary
    assert result.citations == [citation]
    assert result.trace_metadata["tool_source"] == "deterministic_formatter"
    assert result.trace_metadata["citation_count"] == "1"
