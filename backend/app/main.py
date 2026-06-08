from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, auth, documents, evaluation, health, rag, tasks
from app.core.config import get_settings
from app.services.observability import emit_observability_event


settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    documents.preload_selected_ocr_provider()
    yield


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)


@app.middleware("http")
async def observability_request_log(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or f"req_{uuid4().hex}"
    trace_id = request.headers.get("x-trace-id") or request_id
    request.state.request_id = request_id
    request.state.trace_id = trace_id
    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        latency_ms = (perf_counter() - started_at) * 1000
        emit_observability_event(
            get_settings(),
            "api_request",
            "api.request",
            trace_id=trace_id,
            request_id=request_id,
            route=str(request.url.path),
            method=request.method,
            status_code=500,
            latency_ms=round(latency_ms, 2),
            status="error",
            error_code=exc.__class__.__name__,
        )
        raise

    latency_ms = (perf_counter() - started_at) * 1000
    route = request.scope.get("route")
    route_path = getattr(route, "path", str(request.url.path))
    status = "ok"
    if response.status_code >= 500:
        status = "error"
    elif response.status_code >= 400:
        status = "client_error"

    response.headers.setdefault("X-Request-ID", request_id)
    response.headers.setdefault("X-Trace-ID", trace_id)
    emit_observability_event(
        get_settings(),
        "api_request",
        "api.request",
        trace_id=trace_id,
        request_id=request_id,
        route=route_path,
        method=request.method,
        status_code=response.status_code,
        latency_ms=round(latency_ms, 2),
        status=status,
        error_code=None if status == "ok" else f"http_{response.status_code}",
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(agent.router)
app.include_router(evaluation.router)
app.include_router(tasks.router)
