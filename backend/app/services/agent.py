from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.agent import (
    AgentFinalAnswer,
    AgentRun,
    AgentRunRequest,
    AgentRunStatus,
    AgentStep,
    AgentToolCall,
    AgentToolName,
    AgentToolStatus,
)
from app.schemas.documents import ParserStatus
from app.schemas.rag import RagCitation
from app.services.agent_tools import AgentToolService
from app.services.document_storage import DocumentStorage


INVOICE_TASK_KEYWORDS = (
    "invoice",
    "發票",
    "單據",
    "欄位",
    "摘要",
    "整理",
    "summary",
    "summarize",
)

TOOL_TITLES: dict[AgentToolName, str] = {
    "get_document_fields": "Read structured invoice fields",
    "search_documents": "Search supporting document chunks",
    "summarize_invoice_fields": "Summarize invoice fields",
}


class AgentService:
    def __init__(
        self,
        storage: DocumentStorage,
        tool_service: AgentToolService,
    ) -> None:
        self.storage = storage
        self.tool_service = tool_service

    def run(self, request: AgentRunRequest) -> AgentRun:
        created_at = _utc_now()
        tool_calls: list[AgentToolCall] = []
        plan_steps: list[AgentStep] = []
        citations: list[RagCitation] = []
        route = "unsupported_task"
        final_answer = AgentFinalAnswer(
            status=AgentRunStatus.FAILED,
            fallback_reason="unsupported_task",
            text=(
                "This demo Agent only supports invoice summary tasks with a document_id "
                "or document search tasks with a query."
            ),
        )

        if request.document_id:
            route = "invoice_summary"
            final_answer, citations = self._run_invoice_summary(request, tool_calls)
        elif request.query:
            route = "document_question"
            final_answer, citations = self._run_document_question(request, tool_calls)
        else:
            plan_steps.append(
                AgentStep(
                    step_id="step-001",
                    order=1,
                    title="Reject unsupported demo task",
                    status=AgentRunStatus.FAILED,
                    observation_summary="No document_id or query was provided for the demo-safe planner.",
                    fallback_reason="unsupported_task",
                )
            )

        if not plan_steps:
            plan_steps = [
                _step_from_tool_call(tool_call, order)
                for order, tool_call in enumerate(tool_calls, start=1)
            ]

        fallback_count = sum(1 for step in plan_steps if step.fallback_reason)
        updated_at = _utc_now()
        agent_run = AgentRun(
            run_id=f"agent-run-{uuid4()}",
            status=final_answer.status,
            task=request.task,
            document_id=request.document_id,
            query=request.query,
            plan_steps=plan_steps,
            tool_calls=tool_calls,
            final_answer=final_answer,
            citations=citations,
            trace={
                "planner": "deterministic",
                "planner_route": route,
                "tool_policy": "allowlisted_read_only",
                "allowed_tools": "get_document_fields,search_documents,summarize_invoice_fields",
                "tool_count": str(len(tool_calls)),
                "fallback_count": str(fallback_count),
            },
            created_at=created_at,
            updated_at=updated_at,
        )

        return self.storage.save_agent_run(agent_run)

    def _run_invoice_summary(
        self,
        request: AgentRunRequest,
        tool_calls: list[AgentToolCall],
    ) -> tuple[AgentFinalAnswer, list[RagCitation]]:
        assert request.document_id is not None

        fields_call = self.tool_service.get_document_fields(request.document_id)
        tool_calls.append(fields_call)
        parser_result = self.storage.get_parser_result(request.document_id)

        if fields_call.status == AgentToolStatus.FAILED or parser_result is None:
            return (
                AgentFinalAnswer(
                    status=AgentRunStatus.FAILED,
                    fallback_reason=fields_call.observation.fallback_reason or "parser_result_missing",
                    text=_failed_answer(fields_call, tool_calls),
                ),
                [],
            )

        if parser_result.status != ParserStatus.PARSED:
            return (
                AgentFinalAnswer(
                    status=AgentRunStatus.FAILED,
                    fallback_reason=parser_result.fallback_reason or "parser_result_missing",
                    text=_failed_answer(fields_call, tool_calls),
                ),
                [],
            )

        search_query = request.query or _default_invoice_query(request.task)
        search_call = self.tool_service.search_documents(
            search_query,
            top_k=request.top_k,
            document_id=request.document_id,
        )
        tool_calls.append(search_call)

        search_citations = search_call.citations if search_call.status == AgentToolStatus.COMPLETED else []
        summary_call = self.tool_service.summarize_invoice_fields(parser_result, citations=search_citations)
        tool_calls.append(summary_call)

        citations = summary_call.citations or search_citations
        fallback_reason = search_call.observation.fallback_reason or summary_call.observation.fallback_reason

        if summary_call.status == AgentToolStatus.FAILED:
            return (
                AgentFinalAnswer(
                    status=AgentRunStatus.FAILED,
                    fallback_reason=summary_call.observation.fallback_reason or "summary_failed",
                    text=_failed_answer(summary_call, tool_calls),
                ),
                citations,
            )

        return (
            AgentFinalAnswer(
                status=AgentRunStatus.COMPLETED,
                fallback_reason=fallback_reason,
                text=_completed_answer(summary_call.output_summary or "", tool_calls, citations),
            ),
            citations,
        )

    def _run_document_question(
        self,
        request: AgentRunRequest,
        tool_calls: list[AgentToolCall],
    ) -> tuple[AgentFinalAnswer, list[RagCitation]]:
        assert request.query is not None

        search_call = self.tool_service.search_documents(request.query, top_k=request.top_k)
        tool_calls.append(search_call)

        if search_call.status == AgentToolStatus.FAILED:
            return (
                AgentFinalAnswer(
                    status=AgentRunStatus.FAILED,
                    fallback_reason=search_call.observation.fallback_reason or "no_retrieved_chunks",
                    text=_failed_answer(search_call, tool_calls),
                ),
                [],
            )

        answer = str(search_call.output.get("answer") or search_call.output_summary or "")
        return (
            AgentFinalAnswer(
                status=AgentRunStatus.COMPLETED,
                text=_completed_answer(answer, tool_calls, search_call.citations),
            ),
            search_call.citations,
        )


def _step_from_tool_call(tool_call: AgentToolCall, order: int) -> AgentStep:
    status = (
        AgentRunStatus.COMPLETED
        if tool_call.status == AgentToolStatus.COMPLETED
        else AgentRunStatus.FAILED
    )
    return AgentStep(
        step_id=f"step-{order:03d}",
        order=order,
        title=TOOL_TITLES[tool_call.tool_name],
        tool_name=tool_call.tool_name,
        status=status,
        input_summary=tool_call.input_summary,
        observation_summary=tool_call.observation.message,
        fallback_reason=tool_call.observation.fallback_reason,
    )


def _completed_answer(
    answer: str,
    tool_calls: list[AgentToolCall],
    citations: list[RagCitation],
) -> str:
    citation_chunks = ", ".join(citation.chunk_id for citation in citations[:3])
    citation_line = f"Citations: {citation_chunks}." if citation_chunks else "Citations: none available."

    return f"{answer}\n\n{_tool_trace(tool_calls)}\n{citation_line}"


def _failed_answer(failed_tool_call: AgentToolCall, tool_calls: list[AgentToolCall]) -> str:
    fallback_reason = failed_tool_call.observation.fallback_reason or "tool_failed"
    return (
        f"Agent run failed at {failed_tool_call.tool_name}: {failed_tool_call.observation.message} "
        f"Fallback reason: {fallback_reason}.\n\n{_tool_trace(tool_calls)}"
    )


def _tool_trace(tool_calls: list[AgentToolCall]) -> str:
    trace = " -> ".join(f"{tool_call.tool_name}={tool_call.status.value}" for tool_call in tool_calls)
    return f"Tool trace: {trace or 'none'}."


def _default_invoice_query(task: str) -> str:
    normalized_task = task.strip()
    for keyword in INVOICE_TASK_KEYWORDS:
        if keyword.lower() in normalized_task.lower():
            return "invoice payment terms due date total amount"

    return "invoice fields payment terms"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
