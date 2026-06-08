from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EvalDatasetSchemaVersion = Literal["eval_dataset_v1"]
EvalStrategy = Literal["keyword", "vector", "vector_rerank", "hybrid", "hybrid_rerank"]


class EvalFallbackReason(BaseModel):
    reason: str
    count: int


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


class EvalDataset(BaseModel):
    dataset_id: str = Field(..., min_length=1)
    project_id: str | None = Field(default=None, min_length=1)
    name: str = Field(..., min_length=1)
    description: str | None = None
    schema_version: EvalDatasetSchemaVersion = "eval_dataset_v1"
    item_count: int = Field(default=0, ge=0)
    created_at: datetime
    updated_at: datetime


class EvalItem(BaseModel):
    item_id: str = Field(..., min_length=1)
    dataset_id: str = Field(..., min_length=1)
    project_id: str | None = Field(default=None, min_length=1)
    query: str = Field(..., min_length=1)
    expected_terms: list[str] = Field(..., min_length=1)
    expected_document_ids: list[str] = Field(default_factory=list)
    expected_chunk_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class EvalDatasetCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class EvalDatasetUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class EvalItemCreateRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    expected_terms: list[str] = Field(..., min_length=1, max_length=20)
    expected_document_ids: list[str] = Field(default_factory=list, max_length=20)
    expected_chunk_ids: list[str] = Field(default_factory=list, max_length=20)
    tags: list[str] = Field(default_factory=list, max_length=12)
    notes: str | None = Field(default=None, max_length=500)


class EvalItemUpdateRequest(BaseModel):
    query: str | None = Field(default=None, min_length=1, max_length=500)
    expected_terms: list[str] | None = Field(default=None, min_length=1, max_length=20)
    expected_document_ids: list[str] | None = Field(default=None, max_length=20)
    expected_chunk_ids: list[str] | None = Field(default=None, max_length=20)
    tags: list[str] | None = Field(default=None, max_length=12)
    notes: str | None = Field(default=None, max_length=500)


class EvalDatasetListResponse(BaseModel):
    datasets: list[EvalDataset]


class EvalDatasetDetailResponse(BaseModel):
    dataset: EvalDataset
    items: list[EvalItem] = Field(default_factory=list)


class EvalItemListResponse(BaseModel):
    items: list[EvalItem]


class EvalDeleteResponse(BaseModel):
    status: Literal["deleted"] = "deleted"
    dataset_id: str
    item_id: str | None = None


class EvalRunCreateRequest(BaseModel):
    dataset_id: str = Field(..., min_length=1)
    strategies: list[EvalStrategy] = Field(
        default_factory=lambda: ["keyword", "hybrid_rerank", "vector"],
        min_length=1,
        max_length=5,
    )
    top_k: int = Field(default=5, ge=1, le=10)


class EvalRunStrategySummary(BaseModel):
    strategy: EvalStrategy
    case_count: int
    hit_rate_at_k: float
    mrr_at_k: float
    recall_at_k: float
    average_latency_ms: float
    failure_count: int
    fallback_count: int
    trace_metadata_count: int
    result_strategy_counts: dict[str, int] = Field(default_factory=dict)
    fallback_reasons: list[EvalFallbackReason] = Field(default_factory=list)
    environment: dict[str, object] = Field(default_factory=dict)


class EvalRunCaseResult(BaseModel):
    case_id: str
    item_id: str
    strategy: str
    query: str
    top_k: int
    hit: bool
    first_relevant_rank: int | None
    matched_expected_terms: list[str] = Field(default_factory=list)
    error: str | None = None
    fallback_reasons: list[str] = Field(default_factory=list)


class EvalRerankAnalysisRow(BaseModel):
    case_id: str
    item_id: str
    strategy: str
    rank: int
    document_id: str
    filename: str
    chunk_id: str
    text: str
    pre_rerank_rank: int | None = None
    post_rerank_rank: int | None = None
    pre_rerank_score: float | None = None
    rerank_score: float | None = None
    rerank_status: str | None = None
    fallback_state: str | None = None


class EvalRunResponse(BaseModel):
    run_id: str
    dataset_id: str
    dataset_name: str
    project_id: str | None = None
    created_at: str
    top_k: int
    strategies: list[EvalStrategy]
    strategy_summaries: list[EvalRunStrategySummary]


class EvalRunItemsResponse(BaseModel):
    run_id: str
    failed_cases: list[EvalRunCaseResult] = Field(default_factory=list)
    fallback_cases: list[EvalRunCaseResult] = Field(default_factory=list)
    rerank_analysis: list[EvalRerankAnalysisRow] = Field(default_factory=list)
