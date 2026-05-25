from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.routes.auth import require_ingestion_user
from app.core.config import get_settings
from app.schemas.auth import AuthUser
from app.schemas.evaluation import (
    BuiltInRagEvalCaseResult,
    BuiltInRagEvalResponse,
    BuiltInRagEvalSummary,
)
from app.services.evaluation import (
    BUILT_IN_RAG_EVAL_DATASET_NAME,
    RetrievalEvalResult,
    result_fallback_reasons,
    run_built_in_rag_eval,
)


router = APIRouter(prefix="/eval", tags=["eval"])
IngestionUserDep = Annotated[AuthUser | None, Depends(require_ingestion_user)]


@router.post("/rag/built-in", response_model=BuiltInRagEvalResponse)
async def run_built_in_rag_eval_endpoint(
    _auth_user: IngestionUserDep,
) -> BuiltInRagEvalResponse:
    run = run_built_in_rag_eval(get_settings())
    failed_cases = [
        _case_result(result)
        for result in run.results
        if not result.hit or result.error
    ]
    fallback_cases = [
        _case_result(result)
        for result in run.results
        if result_fallback_reasons(result)
    ]

    return BuiltInRagEvalResponse(
        run_id=run.run_id,
        created_at=run.created_at,
        strategy="hybrid_rerank",
        dataset_name=BUILT_IN_RAG_EVAL_DATASET_NAME,
        dataset_path=run.dataset_path,
        case_count=run.case_count,
        summary=BuiltInRagEvalSummary(
            case_count=run.summary.case_count,
            hit_rate_at_k=round(run.summary.hit_rate_at_k, 4),
            mrr_at_k=round(run.summary.mrr_at_k, 4),
            average_latency_ms=round(run.summary.average_latency_ms, 2),
            failure_count=run.summary.failure_count,
            fallback_count=run.summary.fallback_count,
        ),
        environment=run.environment,
        failed_cases=failed_cases,
        fallback_cases=fallback_cases,
    )


def _case_result(result: RetrievalEvalResult) -> BuiltInRagEvalCaseResult:
    return BuiltInRagEvalCaseResult(
        case_id=result.case_id,
        query=result.query,
        top_k=result.top_k,
        hit=result.hit,
        first_relevant_rank=result.first_relevant_rank,
        matched_expected_terms=result.matched_expected_terms,
        error=result.error,
        fallback_reasons=result_fallback_reasons(result),
    )
