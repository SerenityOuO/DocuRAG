from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class BuiltInRagEvalSummary(BaseModel):
    case_count: int
    hit_rate_at_k: float
    mrr_at_k: float
    average_latency_ms: float
    failure_count: int
    fallback_count: int


class BuiltInRagEvalCaseResult(BaseModel):
    case_id: str
    query: str
    top_k: int
    hit: bool
    first_relevant_rank: int | None
    matched_expected_terms: list[str]
    error: str | None
    fallback_reasons: list[str]


class BuiltInRagEvalResponse(BaseModel):
    run_id: str
    created_at: str
    strategy: Literal["hybrid_rerank"]
    dataset_name: str
    dataset_path: str
    case_count: int
    summary: BuiltInRagEvalSummary
    environment: dict[str, object]
    failed_cases: list[BuiltInRagEvalCaseResult]
    fallback_cases: list[BuiltInRagEvalCaseResult]
