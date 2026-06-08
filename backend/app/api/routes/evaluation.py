from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.routes.auth import (
    RequestAuthContext,
    accessible_project_ids,
    require_ingestion_user,
    require_project_access,
)
from app.core.config import get_settings
from app.repositories.document_metadata import create_document_storage
from app.schemas.evaluation import (
    BuiltInRagEvalCaseResult,
    BuiltInRagEvalResponse,
    BuiltInRagEvalSummary,
    EvalDataset,
    EvalDatasetCreateRequest,
    EvalDatasetDetailResponse,
    EvalDatasetListResponse,
    EvalDatasetUpdateRequest,
    EvalDeleteResponse,
    EvalItem,
    EvalItemCreateRequest,
    EvalItemListResponse,
    EvalItemUpdateRequest,
    EvalRunCreateRequest,
    EvalRunItemsResponse,
    EvalRunResponse,
)
from app.services.evaluation import (
    BUILT_IN_RAG_EVAL_DATASET_NAME,
    RetrievalEvalResult,
    result_fallback_reasons,
    run_built_in_rag_eval,
    run_strategy_comparison_eval,
)
from app.services.document_storage import DocumentStorage
from app.services.observability import emit_observability_event


router = APIRouter(prefix="/eval", tags=["eval"])
IngestionUserDep = Annotated[RequestAuthContext | None, Depends(require_ingestion_user)]


def get_document_storage() -> DocumentStorage:
    return create_document_storage(get_settings())


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]


@router.post("/rag/built-in", response_model=BuiltInRagEvalResponse)
async def run_built_in_rag_eval_endpoint(
    http_request: Request,
    auth_user: IngestionUserDep,
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

    response = BuiltInRagEvalResponse(
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
    _emit_eval_metrics(
        http_request=http_request,
        auth_user=auth_user,
        run_id=run.run_id,
        dataset_id=None,
        dataset_name=BUILT_IN_RAG_EVAL_DATASET_NAME,
        strategy="hybrid_rerank",
        summary=response.summary.model_dump(),
        environment=run.environment,
    )
    return response


@router.get("/datasets", response_model=EvalDatasetListResponse)
async def list_eval_datasets(
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalDatasetListResponse:
    return EvalDatasetListResponse(
        datasets=storage.list_eval_datasets(accessible_project_ids(auth_user))
    )


@router.post("/datasets", response_model=EvalDataset)
async def create_eval_dataset(
    request: EvalDatasetCreateRequest,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalDataset:
    try:
        return storage.create_eval_dataset(
            request,
            project_id=auth_user.active_project_id if auth_user is not None and auth_user.auth_mode == "formal" else None,
        )
    except ValueError as exc:
        raise _unprocessable(str(exc)) from exc


@router.get("/datasets/{dataset_id}", response_model=EvalDatasetDetailResponse)
async def get_eval_dataset(
    dataset_id: str,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalDatasetDetailResponse:
    dataset = _get_accessible_dataset(storage, auth_user, dataset_id)
    return EvalDatasetDetailResponse(
        dataset=dataset,
        items=storage.list_eval_items(dataset.dataset_id),
    )


@router.patch("/datasets/{dataset_id}", response_model=EvalDataset)
async def update_eval_dataset(
    dataset_id: str,
    request: EvalDatasetUpdateRequest,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalDataset:
    _get_accessible_dataset(storage, auth_user, dataset_id)
    try:
        dataset = storage.update_eval_dataset(dataset_id, request)
    except ValueError as exc:
        raise _unprocessable(str(exc)) from exc

    if dataset is None:
        raise _not_found("Eval dataset not found.")

    return dataset


@router.delete("/datasets/{dataset_id}", response_model=EvalDeleteResponse)
async def delete_eval_dataset(
    dataset_id: str,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalDeleteResponse:
    _get_accessible_dataset(storage, auth_user, dataset_id)
    if not storage.delete_eval_dataset(dataset_id):
        raise _not_found("Eval dataset not found.")

    return EvalDeleteResponse(dataset_id=dataset_id)


@router.get("/datasets/{dataset_id}/items", response_model=EvalItemListResponse)
async def list_eval_items(
    dataset_id: str,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalItemListResponse:
    dataset = _get_accessible_dataset(storage, auth_user, dataset_id)
    return EvalItemListResponse(items=storage.list_eval_items(dataset.dataset_id))


@router.post("/datasets/{dataset_id}/items", response_model=EvalItem)
async def create_eval_item(
    dataset_id: str,
    request: EvalItemCreateRequest,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalItem:
    dataset = _get_accessible_dataset(storage, auth_user, dataset_id)
    try:
        return storage.create_eval_item(dataset, request)
    except ValueError as exc:
        raise _unprocessable(str(exc)) from exc


@router.get("/datasets/{dataset_id}/items/{item_id}", response_model=EvalItem)
async def get_eval_item(
    dataset_id: str,
    item_id: str,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalItem:
    dataset = _get_accessible_dataset(storage, auth_user, dataset_id)
    item = storage.get_eval_item(dataset.dataset_id, item_id)
    if item is None:
        raise _not_found("Eval item not found.")

    return item


@router.patch("/datasets/{dataset_id}/items/{item_id}", response_model=EvalItem)
async def update_eval_item(
    dataset_id: str,
    item_id: str,
    request: EvalItemUpdateRequest,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalItem:
    dataset = _get_accessible_dataset(storage, auth_user, dataset_id)
    try:
        item = storage.update_eval_item(dataset.dataset_id, item_id, request)
    except ValueError as exc:
        raise _unprocessable(str(exc)) from exc

    if item is None:
        raise _not_found("Eval item not found.")

    return item


@router.delete("/datasets/{dataset_id}/items/{item_id}", response_model=EvalDeleteResponse)
async def delete_eval_item(
    dataset_id: str,
    item_id: str,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalDeleteResponse:
    dataset = _get_accessible_dataset(storage, auth_user, dataset_id)
    if not storage.delete_eval_item(dataset.dataset_id, item_id):
        raise _not_found("Eval item not found.")

    return EvalDeleteResponse(dataset_id=dataset.dataset_id, item_id=item_id)


@router.post("/runs", response_model=EvalRunResponse)
async def run_eval_strategy_comparison(
    http_request: Request,
    request: EvalRunCreateRequest,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalRunResponse:
    dataset = _get_accessible_dataset(storage, auth_user, request.dataset_id)
    items = storage.list_eval_items(dataset.dataset_id)
    try:
        run = run_strategy_comparison_eval(
            dataset=dataset,
            items=items,
            documents=storage.list_documents_for_rag(accessible_project_ids(auth_user)),
            strategies=request.strategies,
            top_k=request.top_k,
            settings=get_settings(),
        )
    except ValueError as exc:
        raise _unprocessable(str(exc)) from exc

    storage.save_eval_run(run)
    for summary in run["strategy_summaries"]:
        _emit_eval_metrics(
            http_request=http_request,
            auth_user=auth_user,
            run_id=str(run["run_id"]),
            dataset_id=str(run["dataset_id"]),
            dataset_name=str(run["dataset_name"]),
            strategy=str(summary["strategy"]),
            summary=summary,
            environment=summary.get("environment") if isinstance(summary.get("environment"), dict) else {},
        )
    return EvalRunResponse.model_validate(run)


@router.get("/runs/{run_id}", response_model=EvalRunResponse)
async def get_eval_run(
    run_id: str,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalRunResponse:
    run = _get_accessible_run(storage, auth_user, run_id)
    return EvalRunResponse.model_validate(run)


@router.get("/runs/{run_id}/items", response_model=EvalRunItemsResponse)
async def get_eval_run_items(
    run_id: str,
    storage: DocumentStorageDep,
    auth_user: IngestionUserDep,
) -> EvalRunItemsResponse:
    run = _get_accessible_run(storage, auth_user, run_id)
    return EvalRunItemsResponse.model_validate(run)


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


def _get_accessible_dataset(
    storage: DocumentStorage,
    auth_user: RequestAuthContext | None,
    dataset_id: str,
) -> EvalDataset:
    dataset = storage.get_eval_dataset(dataset_id)
    if dataset is None:
        raise _not_found("Eval dataset not found.")

    require_project_access(auth_user, dataset.project_id)
    return dataset


def _get_accessible_run(
    storage: DocumentStorage,
    auth_user: RequestAuthContext | None,
    run_id: str,
) -> dict[str, object]:
    run = storage.get_eval_run(run_id)
    if run is None:
        raise _not_found("Eval run not found.")

    project_id = run.get("project_id")
    require_project_access(auth_user, str(project_id) if project_id else None)
    return run


def _not_found(message: str) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={
            "status": "not_found",
            "error": message,
        },
    )


def _unprocessable(message: str) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "status": "invalid_input",
            "error": message,
        },
    )


def _emit_eval_metrics(
    *,
    http_request: Request,
    auth_user: RequestAuthContext | None,
    run_id: str,
    dataset_id: str | None,
    dataset_name: str,
    strategy: str,
    summary: dict[str, object],
    environment: dict[str, object],
) -> None:
    emit_observability_event(
        get_settings(),
        "eval_metrics",
        "eval.run",
        trace_id=getattr(http_request.state, "trace_id", None),
        request_id=getattr(http_request.state, "request_id", None),
        organization_id=auth_user.organization_id if auth_user is not None else None,
        project_id=auth_user.active_project_id if auth_user is not None else None,
        actor_user_id=auth_user.username if auth_user is not None else None,
        document_id=None,
        strategy=strategy,
        provider=str(environment.get("retrieval_provider") or strategy),
        latency_ms=summary.get("average_latency_ms"),
        status="completed",
        error_code=None,
        run_id=run_id,
        dataset_id=dataset_id,
        dataset_name=dataset_name,
        case_count=summary.get("case_count"),
        hit_rate_at_k=summary.get("hit_rate_at_k"),
        mrr_at_k=summary.get("mrr_at_k"),
        recall_at_k=summary.get("recall_at_k"),
        average_latency_ms=summary.get("average_latency_ms"),
        failure_count=summary.get("failure_count"),
        fallback_count=summary.get("fallback_count"),
        trace_metadata_count=summary.get("trace_metadata_count"),
    )
