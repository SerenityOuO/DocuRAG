from dataclasses import dataclass
from typing import Literal

from app.schemas.agent import AgentToolCall, AgentToolName, AgentToolObservation, AgentToolStatus
from app.schemas.documents import DocumentFields, ExtractedField, ParserResult, ParserStatus
from app.schemas.rag import RagCitation
from app.services.document_storage import DocumentStorage
from app.services.rag import KeywordRagProvider, RagProvider


INVOICE_FIELD_NAMES = [
    "document_type",
    "vendor_name",
    "invoice_number",
    "issue_date",
    "total_amount",
    "tax_amount",
    "currency",
]

ToolTier = Literal["read-only", "write", "admin", "destructive"]
RiskTier = Literal["low", "medium", "high", "prohibited"]
ApprovalState = Literal["not_required", "required", "approved", "rejected", "expired"]


@dataclass(frozen=True)
class AgentToolPolicy:
    tool_name: AgentToolName
    tier: ToolTier
    required_roles: tuple[str, ...]
    permission_requirement: str
    side_effect_policy: str
    risk_tier: RiskTier = "low"
    risk_score: int = 10
    approval_required: bool = False
    approval_state: ApprovalState = "not_required"
    human_confirmation_required: str = "not_required"
    human_confirmation_status: str = "not_required"
    project_access_required: bool = True


@dataclass(frozen=True)
class AgentToolPermissionDecision:
    tool_name: AgentToolName
    policy: AgentToolPolicy
    decision: Literal["allowed", "forbidden"]
    reason: str
    role: str | None
    project_id: str | None
    project_access: str

    @property
    def allowed(self) -> bool:
        return self.decision == "allowed"

    def trace_metadata(self) -> dict[str, str]:
        return {
            **tool_policy_metadata(self.policy),
            "permission_decision": self.decision,
            "permission_reason": self.reason,
            "role": self.role or "auth_disabled",
            "project_id": self.project_id or "not_applicable",
            "project_access": self.project_access,
        }


AGENT_TOOL_POLICIES: dict[AgentToolName, AgentToolPolicy] = {
    "get_document_fields": AgentToolPolicy(
        tool_name="get_document_fields",
        tier="read-only",
        required_roles=("admin", "analyst"),
        permission_requirement="agent_run_tool_execution",
        side_effect_policy="no_side_effects",
    ),
    "search_documents": AgentToolPolicy(
        tool_name="search_documents",
        tier="read-only",
        required_roles=("admin", "analyst"),
        permission_requirement="agent_run_tool_execution",
        side_effect_policy="no_side_effects",
    ),
    "summarize_invoice_fields": AgentToolPolicy(
        tool_name="summarize_invoice_fields",
        tier="read-only",
        required_roles=("admin", "analyst"),
        permission_requirement="agent_run_tool_execution",
        side_effect_policy="no_side_effects",
    ),
}


def evaluate_agent_tool_permission(
    tool_name: AgentToolName,
    *,
    role: str | None,
    project_id: str | None,
) -> AgentToolPermissionDecision:
    policy = AGENT_TOOL_POLICIES[tool_name]
    project_access = "checked" if project_id else "not_required"

    if policy.tier == "destructive" or policy.risk_tier == "prohibited":
        return AgentToolPermissionDecision(
            tool_name=tool_name,
            policy=policy,
            decision="forbidden",
            reason="destructive_tool_prohibited",
            role=role,
            project_id=project_id,
            project_access=project_access,
        )

    if role is not None and role not in policy.required_roles:
        return AgentToolPermissionDecision(
            tool_name=tool_name,
            policy=policy,
            decision="forbidden",
            reason="tool_permission_forbidden",
            role=role,
            project_id=project_id,
            project_access=project_access,
        )

    if policy.approval_required and policy.approval_state != "approved":
        return AgentToolPermissionDecision(
            tool_name=tool_name,
            policy=policy,
            decision="forbidden",
            reason=_approval_forbidden_reason(policy.approval_state),
            role=role,
            project_id=project_id,
            project_access=project_access,
        )

    reason = "role_allowed" if role else "auth_disabled_or_local"
    return AgentToolPermissionDecision(
        tool_name=tool_name,
        policy=policy,
        decision="allowed",
        reason=reason,
        role=role,
        project_id=project_id,
        project_access=project_access,
    )


def _approval_forbidden_reason(approval_state: ApprovalState) -> str:
    if approval_state == "rejected":
        return "approval_rejected"
    if approval_state == "expired":
        return "approval_expired"
    return "approval_required"


def tool_policy_metadata(policy: AgentToolPolicy) -> dict[str, str]:
    return {
        "tool_tier": policy.tier,
        "required_roles": ",".join(policy.required_roles),
        "permission_requirement": policy.permission_requirement,
        "side_effect_policy": policy.side_effect_policy,
        "risk_tier": policy.risk_tier,
        "risk_score": str(policy.risk_score),
        "approval_required": "true" if policy.approval_required else "false",
        "approval_state": policy.approval_state,
        "human_confirmation_required": policy.human_confirmation_required,
        "human_confirmation_status": policy.human_confirmation_status,
        "destructive": "true" if policy.tier == "destructive" else "false",
    }


class AgentToolService:
    def __init__(
        self,
        storage: DocumentStorage,
        rag_provider: RagProvider | None = None,
        project_ids: frozenset[str] | None = None,
    ) -> None:
        self.storage = storage
        self.rag_provider = rag_provider or KeywordRagProvider()
        self.project_ids = project_ids

    def get_document_fields(self, document_id: str) -> AgentToolCall:
        trace_metadata = self._trace_metadata("get_document_fields", "local_metadata")
        parser_result = self.storage.get_parser_result(document_id)

        if parser_result is None:
            return self._failed_tool_call(
                "get_document_fields",
                f"document_id={document_id}",
                "Document not found.",
                "document_not_found",
                trace_metadata,
            )

        missing_fields = _missing_invoice_fields(parser_result.fields)
        output = {
            "document_id": parser_result.document_id,
            "parser_status": parser_result.status.value,
            "parser_source": parser_result.parser_source,
            "schema_version": parser_result.schema_version,
            "fields": parser_result.fields.model_dump(mode="json"),
            "missing_fields": missing_fields,
            "fallback_reason": parser_result.fallback_reason,
        }

        if parser_result.status != ParserStatus.PARSED:
            return AgentToolCall(
                tool_name="get_document_fields",
                status=AgentToolStatus.FAILED,
                input_summary=f"document_id={document_id}",
                output_summary=f"Parser result status is {parser_result.status.value}.",
                observation=AgentToolObservation(
                    status=AgentToolStatus.FAILED,
                    message="Parser result is not available for this document.",
                    missing_fields=missing_fields,
                    fallback_reason=parser_result.fallback_reason or "parser_result_missing",
                ),
                output=output,
                trace_metadata={
                    **trace_metadata,
                    "parser_status": parser_result.status.value,
                    "missing_field_count": str(len(missing_fields)),
                },
                error_message=parser_result.error_message,
            )

        return AgentToolCall(
            tool_name="get_document_fields",
            status=AgentToolStatus.COMPLETED,
            input_summary=f"document_id={document_id}",
            output_summary=_invoice_fields_summary(parser_result.fields),
            observation=AgentToolObservation(
                status=AgentToolStatus.COMPLETED,
                message="Parser result was available.",
                missing_fields=missing_fields,
                fallback_reason=parser_result.fallback_reason,
            ),
            output=output,
            trace_metadata={
                **trace_metadata,
                "parser_status": parser_result.status.value,
                "missing_field_count": str(len(missing_fields)),
            },
        )

    def search_documents(
        self,
        query: str,
        top_k: int = 3,
        document_id: str | None = None,
    ) -> AgentToolCall:
        trace_metadata = self._trace_metadata("search_documents", "rag_provider")
        documents = self.storage.list_documents_for_rag(self.project_ids)

        if document_id is not None:
            documents = [document for document in documents if document.document_id == document_id]
            if not documents:
                return self._failed_tool_call(
                    "search_documents",
                    f"query={query}; document_id={document_id}; top_k={top_k}",
                    "Document not found for search.",
                    "document_not_found",
                    trace_metadata,
                )

        try:
            response = self.rag_provider.query(query, top_k, documents)
        except Exception as exc:
            return self._failed_tool_call(
                "search_documents",
                f"query={query}; document_id={document_id or 'any'}; top_k={top_k}",
                "Document search failed.",
                "tool_error",
                trace_metadata,
                error_message=str(exc),
            )

        output = {
            "answer": response.answer,
            "citations": [citation.model_dump(mode="json") for citation in response.citations],
            "retrieved_chunks": [chunk.model_dump(mode="json") for chunk in response.retrieved_chunks],
        }
        metadata = {
            **trace_metadata,
            "rag_provider": getattr(self.rag_provider, "name", self.rag_provider.__class__.__name__),
            "retrieved_chunk_count": str(len(response.retrieved_chunks)),
            "citation_count": str(len(response.citations)),
        }

        if not response.retrieved_chunks:
            return AgentToolCall(
                tool_name="search_documents",
                status=AgentToolStatus.FAILED,
                input_summary=f"query={query}; document_id={document_id or 'any'}; top_k={top_k}",
                output_summary="No document chunks matched the query.",
                observation=AgentToolObservation(
                    status=AgentToolStatus.FAILED,
                    message="No document chunks matched the query.",
                    fallback_reason="no_retrieved_chunks",
                ),
                output=output,
                trace_metadata=metadata,
            )

        return AgentToolCall(
            tool_name="search_documents",
            status=AgentToolStatus.COMPLETED,
            input_summary=f"query={query}; document_id={document_id or 'any'}; top_k={top_k}",
            output_summary=f"Retrieved {len(response.retrieved_chunks)} chunk(s).",
            observation=AgentToolObservation(
                status=AgentToolStatus.COMPLETED,
                message="Document search returned matching chunks.",
            ),
            output=output,
            citations=response.citations,
            retrieved_chunks=response.retrieved_chunks,
            trace_metadata=metadata,
        )

    def summarize_invoice_fields(
        self,
        parser_result: ParserResult,
        citations: list[RagCitation] | None = None,
    ) -> AgentToolCall:
        trace_metadata = self._trace_metadata("summarize_invoice_fields", "deterministic_formatter")
        missing_fields = _missing_invoice_fields(parser_result.fields)

        if parser_result.status != ParserStatus.PARSED:
            return AgentToolCall(
                tool_name="summarize_invoice_fields",
                status=AgentToolStatus.FAILED,
                input_summary=f"document_id={parser_result.document_id}",
                output_summary=f"Parser result status is {parser_result.status.value}.",
                observation=AgentToolObservation(
                    status=AgentToolStatus.FAILED,
                    message="Cannot summarize invoice fields before parser result is available.",
                    missing_fields=missing_fields,
                    fallback_reason=parser_result.fallback_reason or "parser_result_missing",
                ),
                output={
                    "document_id": parser_result.document_id,
                    "parser_status": parser_result.status.value,
                    "missing_fields": missing_fields,
                },
                trace_metadata={
                    **trace_metadata,
                    "parser_status": parser_result.status.value,
                    "missing_field_count": str(len(missing_fields)),
                },
                error_message=parser_result.error_message,
            )

        summary = _build_invoice_summary(parser_result.fields, citations or [], missing_fields)
        return AgentToolCall(
            tool_name="summarize_invoice_fields",
            status=AgentToolStatus.COMPLETED,
            input_summary=f"document_id={parser_result.document_id}",
            output_summary=summary,
            observation=AgentToolObservation(
                status=AgentToolStatus.COMPLETED,
                message="Invoice fields were summarized with deterministic formatting.",
                missing_fields=missing_fields,
                fallback_reason=parser_result.fallback_reason,
            ),
            output={
                "document_id": parser_result.document_id,
                "summary": summary,
                "missing_fields": missing_fields,
            },
            citations=citations or [],
            trace_metadata={
                **trace_metadata,
                "parser_status": parser_result.status.value,
                "missing_field_count": str(len(missing_fields)),
                "citation_count": str(len(citations or [])),
            },
        )

    def _trace_metadata(self, tool_name: AgentToolName, tool_source: str) -> dict[str, str]:
        policy = AGENT_TOOL_POLICIES[tool_name]
        return {
            "tool_name": tool_name,
            "tool_source": tool_source,
            "allowlisted": "true",
            "read_only": "true",
            **tool_policy_metadata(policy),
        }

    def _failed_tool_call(
        self,
        tool_name: AgentToolName,
        input_summary: str,
        message: str,
        fallback_reason: str,
        trace_metadata: dict[str, str],
        error_message: str | None = None,
    ) -> AgentToolCall:
        return AgentToolCall(
            tool_name=tool_name,
            status=AgentToolStatus.FAILED,
            input_summary=input_summary,
            output_summary=message,
            observation=AgentToolObservation(
                status=AgentToolStatus.FAILED,
                message=message,
                fallback_reason=fallback_reason,
            ),
            trace_metadata={**trace_metadata, "fallback_reason": fallback_reason},
            error_message=error_message,
        )


def _field_display_value(field: ExtractedField) -> str | None:
    if field.value is None:
        return None

    return str(field.value)


def _missing_invoice_fields(fields: DocumentFields) -> list[str]:
    missing_fields = [
        field_name
        for field_name in INVOICE_FIELD_NAMES
        if getattr(fields, field_name).value is None
    ]

    if not fields.line_items:
        missing_fields.append("line_items")

    return missing_fields


def _invoice_fields_summary(fields: DocumentFields) -> str:
    parts = []
    invoice_number = _field_display_value(fields.invoice_number)
    vendor_name = _field_display_value(fields.vendor_name)
    total_amount = _field_display_value(fields.total_amount)
    currency = _field_display_value(fields.currency)

    if invoice_number:
        parts.append(f"invoice_number={invoice_number}")
    if vendor_name:
        parts.append(f"vendor={vendor_name}")
    if total_amount:
        total = f"{total_amount} {currency}".strip() if currency else total_amount
        parts.append(f"total={total}")

    return "; ".join(parts) if parts else "No invoice fields were populated."


def _build_invoice_summary(
    fields: DocumentFields,
    citations: list[RagCitation],
    missing_fields: list[str],
) -> str:
    lines = []
    invoice_number = _field_display_value(fields.invoice_number) or "unknown invoice number"
    vendor_name = _field_display_value(fields.vendor_name) or "unknown vendor"
    issue_date = _field_display_value(fields.issue_date)
    total_amount = _field_display_value(fields.total_amount)
    tax_amount = _field_display_value(fields.tax_amount)
    currency = _field_display_value(fields.currency)

    lines.append(f"Invoice {invoice_number} is from {vendor_name}.")
    if issue_date:
        lines.append(f"Issue date: {issue_date}.")
    if total_amount:
        total = f"{total_amount} {currency}".strip() if currency else total_amount
        lines.append(f"Total amount: {total}.")
    if tax_amount:
        tax = f"{tax_amount} {currency}".strip() if currency else tax_amount
        lines.append(f"Tax amount: {tax}.")
    if citations:
        citation_chunks = ", ".join(citation.chunk_id for citation in citations[:3])
        lines.append(f"Source chunks: {citation_chunks}.")
    if missing_fields:
        lines.append(f"Missing fields: {', '.join(missing_fields)}.")

    return " ".join(lines)
