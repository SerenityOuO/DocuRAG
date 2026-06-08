from __future__ import annotations

from dataclasses import dataclass, field
import json
from time import perf_counter
from typing import Literal, Protocol

from pydantic import BaseModel, Field, ValidationError

from app.core.config import Settings
from app.schemas.agent import AgentRunRequest, AgentToolName
from app.services.llm import LlmGeneration, LlmProvider, LlmProviderError, create_llm_provider


AgentPlanRoute = Literal["invoice_summary", "document_question", "unsupported_task"]
AgentPlannerStatus = Literal["completed", "fallback"]
AgentPlanValidationStatus = Literal["valid", "invalid", "timeout", "unavailable", "disabled"]

ALLOWED_AGENT_TOOLS: tuple[AgentToolName, ...] = (
    "get_document_fields",
    "search_documents",
    "summarize_invoice_fields",
)


@dataclass(frozen=True)
class AgentPlannerContext:
    role: str | None = None
    project_id: str | None = None
    allowed_tools: tuple[AgentToolName, ...] = ALLOWED_AGENT_TOOLS


@dataclass(frozen=True)
class AgentPlan:
    route: AgentPlanRoute
    tool_names: tuple[AgentToolName, ...]
    planner_provider: str
    attempted_provider: str
    status: AgentPlannerStatus
    validation_status: AgentPlanValidationStatus
    fallback_reason: str | None = None
    latency_ms: float | None = None
    audit_metadata: dict[str, str] = field(default_factory=dict)


class AgentPlanner(Protocol):
    def plan(self, request: AgentRunRequest, context: AgentPlannerContext) -> AgentPlan:
        pass


class DeterministicAgentPlanner:
    provider_name = "deterministic"

    def plan(self, request: AgentRunRequest, context: AgentPlannerContext) -> AgentPlan:
        route = _deterministic_route(request)
        return AgentPlan(
            route=route,
            tool_names=_safe_tools_for_route(route),
            planner_provider=self.provider_name,
            attempted_provider=self.provider_name,
            status="completed",
            validation_status="valid",
        )


class LlmAgentPlanner:
    provider_name = "llm_planner"

    def __init__(
        self,
        llm_provider: LlmProvider,
        fallback_planner: AgentPlanner | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.fallback_planner = fallback_planner or DeterministicAgentPlanner()

    def plan(self, request: AgentRunRequest, context: AgentPlannerContext) -> AgentPlan:
        started_at = perf_counter()
        try:
            generation = self.llm_provider.generate(
                _planner_prompt(request, context),
                system=(
                    "You are a DocuRAG Agent planner. Return one JSON object only. "
                    "Select only allowed tools and never invent SQL, shell, filesystem, network or destructive tools."
                ),
            )
            llm_plan = _parse_llm_plan(generation.text)
            route, tool_names = _validate_llm_plan(llm_plan, request, context)
        except (LlmProviderError, TimeoutError) as exc:
            validation_status: AgentPlanValidationStatus = (
                "timeout" if _looks_like_timeout(exc) else "unavailable"
            )
            fallback_reason = "llm_planner_timeout" if validation_status == "timeout" else "llm_planner_unavailable"
            return self._fallback_plan(
                request,
                context,
                validation_status=validation_status,
                fallback_reason=fallback_reason,
                latency_ms=_elapsed_ms(started_at),
            )
        except (ValueError, ValidationError) as exc:
            return self._fallback_plan(
                request,
                context,
                validation_status="invalid",
                fallback_reason=f"llm_planner_invalid_plan:{_compact_error(exc)}",
                latency_ms=_elapsed_ms(started_at),
            )

        return AgentPlan(
            route=route,
            tool_names=tool_names,
            planner_provider=self.provider_name,
            attempted_provider=self.provider_name,
            status="completed",
            validation_status="valid",
            latency_ms=_elapsed_ms(started_at),
            audit_metadata=_generation_metadata(generation),
        )

    def _fallback_plan(
        self,
        request: AgentRunRequest,
        context: AgentPlannerContext,
        *,
        validation_status: AgentPlanValidationStatus,
        fallback_reason: str,
        latency_ms: float,
    ) -> AgentPlan:
        fallback = self.fallback_planner.plan(request, context)
        return AgentPlan(
            route=fallback.route,
            tool_names=fallback.tool_names,
            planner_provider=fallback.planner_provider,
            attempted_provider=self.provider_name,
            status="fallback",
            validation_status=validation_status,
            fallback_reason=fallback_reason,
            latency_ms=latency_ms,
            audit_metadata={"fallback_provider": fallback.planner_provider},
        )


class _LlmPlanStep(BaseModel):
    tool_name: AgentToolName


class _LlmPlanResponse(BaseModel):
    route: AgentPlanRoute
    steps: list[_LlmPlanStep] = Field(default_factory=list)


def create_agent_planner(
    settings: Settings,
    llm_provider: LlmProvider | None = None,
) -> AgentPlanner:
    provider_name = (settings.agent_planner_provider or "").strip().lower()

    if provider_name in {"", "deterministic", "disabled", "none"}:
        return DeterministicAgentPlanner()

    if provider_name in {"llm", "llm_planner"}:
        return LlmAgentPlanner(llm_provider or create_llm_provider(settings))

    return DeterministicAgentPlanner()


def agent_plan_trace(plan: AgentPlan) -> dict[str, str]:
    trace = {
        "planner": plan.planner_provider,
        "planner_provider": plan.planner_provider,
        "planner_attempted_provider": plan.attempted_provider,
        "planner_status": plan.status,
        "plan_validation_status": plan.validation_status,
        "planned_tools": ",".join(plan.tool_names),
    }
    if plan.fallback_reason:
        trace["planner_fallback_reason"] = plan.fallback_reason
    if plan.latency_ms is not None:
        trace["planner_latency_ms"] = f"{plan.latency_ms:.2f}"
    trace.update(plan.audit_metadata)
    return trace


def _planner_prompt(request: AgentRunRequest, context: AgentPlannerContext) -> str:
    payload = {
        "task": request.task,
        "document_id": request.document_id,
        "query": request.query,
        "top_k": request.top_k,
        "role": context.role or "unknown",
        "project_id": context.project_id,
        "allowed_tools": list(context.allowed_tools),
        "valid_routes": ["invoice_summary", "document_question", "unsupported_task"],
        "response_schema": {
            "route": "invoice_summary | document_question | unsupported_task",
            "steps": [{"tool_name": "one allowed tool name"}],
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _parse_llm_plan(text: str) -> _LlmPlanResponse:
    cleaned = text.strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("response_missing_json_object")
    data = json.loads(cleaned[start : end + 1])
    return _LlmPlanResponse.model_validate(data)


def _validate_llm_plan(
    llm_plan: _LlmPlanResponse,
    request: AgentRunRequest,
    context: AgentPlannerContext,
) -> tuple[AgentPlanRoute, tuple[AgentToolName, ...]]:
    route = llm_plan.route
    tool_names = tuple(step.tool_name for step in llm_plan.steps)
    allowed_tools = set(context.allowed_tools)

    if any(tool_name not in allowed_tools for tool_name in tool_names):
        raise ValueError("tool_not_allowed")

    expected_tools = _safe_tools_for_route(route)
    if tool_names != expected_tools:
        raise ValueError("plan_tools_do_not_match_safe_route")

    if route == "invoice_summary" and not request.document_id:
        raise ValueError("invoice_summary_requires_document_id")

    if route == "document_question" and not request.query:
        raise ValueError("document_question_requires_query")

    deterministic_route = _deterministic_route(request)
    if route != deterministic_route:
        raise ValueError("plan_route_does_not_match_safe_inputs")

    return route, tool_names


def _deterministic_route(request: AgentRunRequest) -> AgentPlanRoute:
    if request.document_id:
        return "invoice_summary"
    if request.query:
        return "document_question"
    return "unsupported_task"


def _safe_tools_for_route(route: AgentPlanRoute) -> tuple[AgentToolName, ...]:
    if route == "invoice_summary":
        return ("get_document_fields", "search_documents", "summarize_invoice_fields")
    if route == "document_question":
        return ("search_documents",)
    return ()


def _generation_metadata(generation: LlmGeneration) -> dict[str, str]:
    metadata = {
        "planner_model": generation.model,
        "planner_llm_provider": str(generation.raw.get("provider") or ""),
    }
    optional_values = {
        "planner_prompt_tokens": generation.prompt_tokens,
        "planner_completion_tokens": generation.completion_tokens,
        "planner_total_tokens": generation.total_tokens,
        "planner_provider_latency_ms": generation.provider_latency_ms,
        "planner_provider_request_id": generation.provider_request_id,
    }
    for key, value in optional_values.items():
        if value is not None:
            metadata[key] = f"{value:.2f}" if isinstance(value, float) else str(value)
    return {key: value for key, value in metadata.items() if value}


def _looks_like_timeout(exc: BaseException) -> bool:
    return isinstance(exc, TimeoutError) or "timed out" in str(exc).lower() or "timeout" in str(exc).lower()


def _compact_error(exc: BaseException) -> str:
    return str(exc).splitlines()[0][:120] or exc.__class__.__name__


def _elapsed_ms(started_at: float) -> float:
    return (perf_counter() - started_at) * 1000
