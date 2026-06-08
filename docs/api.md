# API Draft

此文件先定義 MVP API 邊界，實作時可依 ticket 逐步補齊。

## System

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |

## Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Phase 28 demo login; available only when `DOCURAG_AUTH_MODE=demo` |
| POST | `/auth/logout` | Stateless demo logout response; frontend clears its local token |
| GET | `/auth/me` | Current demo auth mode and user |

Phase 28 demo auth mode is disabled by default. Set `DOCURAG_AUTH_MODE=demo` to enable fixed local demo users:

| Username | Role | Demo usage |
|---|---|---|
| `admin` | `admin` | Can upload, OCR, parse, vector index, download and query. |
| `analyst` | `analyst` | Can upload, OCR, parse, vector index, download and query. |
| `viewer` | `viewer` | Can query and download existing files, but cannot run ingestion write APIs. |

`POST /auth/login` returns a bearer token and user object, never a password. In demo mode, write / ingestion endpoints require `Authorization: Bearer {token}`. Viewer receives 403 forbidden for upload, provider-selected OCR, mock OCR, parse and vector index. Download requires login in demo mode but is allowed for all three demo roles.

This is a demo-safe auth slice, not production JWT refresh rotation, PostgreSQL users table, SSO, OAuth, MFA, tenant isolation, project permission, Redis session or formal RBAC.

## Phase 32 Auth / RBAC Contract

`32-01` defines the formal Auth / RBAC / tenant boundary contract. `32-02` adds the PostgreSQL schema foundation for users, organizations, projects, roles and memberships, but it does not change current endpoint guard behavior, enable Redis session storage, or replace Phase 28 demo auth. Runtime permission enforcement is split into later Phase 32 tickets.

### Domain Boundary

| Domain | Contract | Notes |
|---|---|---|
| User | Human account that can authenticate and receive project access. | Schema foundation exists after `32-02`; production login runtime is deferred. |
| Organization | Top-level tenant boundary that owns projects and memberships. | All cross-organization access must be denied by backend guards. |
| Project | Workspace boundary for documents, eval runs, Agent runs and future Qdrant payload filters. | Existing nullable `project_id` metadata from Phase 31 becomes the join point. |
| Role | Permission tier assigned inside a project. | Supported contract roles are `viewer`, `analyst` and `admin`. |
| Membership | User-to-organization / project relationship with role and status. | Disabled or removed memberships must not retain access. |
| Project access | Backend-enforced check before returning or mutating project-scoped resources. | Frontend role surface is advisory only; backend remains authoritative. |

### Role Permission Matrix

| Capability | Viewer | Analyst | Admin |
|---|---:|---:|---:|
| Login / read own user context | yes | yes | yes |
| List accessible projects | yes | yes | yes |
| Query existing project documents with RAG | yes | yes | yes |
| Download documents in accessible projects | yes | yes | yes |
| Upload documents | no | yes | yes |
| Run OCR / parser / vector indexing | no | yes | yes |
| Run built-in eval for accessible project data | no | yes | yes |
| Run deterministic Agent tools on accessible project data | no | yes | yes |
| Manage project metadata / memberships | no | no | yes |
| Access another organization or project without membership | no | no | no |

### API Guard Policy

| API group | Guard contract |
|---|---|
| Auth endpoints | Public login endpoint; authenticated `me` endpoint returns user, memberships and active project context. |
| Read endpoints | Require authenticated user and project membership; response must be filtered by project access. |
| Ingestion write endpoints | Require Analyst or Admin role for the target project. Viewer receives `403 forbidden`. |
| Admin / membership endpoints | Require Admin role for the target project or organization. |
| Cross-project access | Must return unauthorized / forbidden without leaking whether the target resource exists. |

Demo auth remains a local validation fallback. It may keep fixed users and stateless tokens for smoke tests, but documentation and UI must not call it production RBAC. Formal Auth / RBAC must not silently depend on Phase 28 demo users.

SSO, OAuth, MFA, password reset, email verification, Redis-backed session storage, refresh token rotation and production audit pipeline are explicitly outside `32-01` scope.

`32-02` status: the formal schema foundation and explicit migration command exist, including demo seed users and a disabled user record with password-hash persistence. Endpoint permission guards, cross-project filtering enforcement and frontend role surface remain deferred to `32-03` / `32-04`.

`32-03` status: backend permission guards are connected for formal signed bearer tokens when `DOCURAG_AUTH_MODE=formal`. Formal tokens must include `sub`, `display_name`, `role`, `organization_id`, `project_ids` and active `project_id`; `/auth/login` still does not implement production login in formal mode. Document reads, downloads, OCR, parser, vector indexing, RAG query and Agent lookup are filtered or denied by project access. Document upload, OCR, parser, vector indexing, built-in eval and Agent run require Analyst or Admin. Viewer receives a generic `403 forbidden`; cross-project denied responses do not include target document or project identifiers.

## Phase 33 Redis / NATS Worker Task Contract

`33-01` defines the Redis / NATS worker task contract. `33-02` adds only an opt-in Redis backend slice for session cache, RAG query cache and rate limit. `33-03` adds a demo-safe NATS helper, worker skeleton and task status store / API. If `DOCURAG_REDIS_URL` or `DOCURAG_NATS_URL` is empty, those runtimes are disabled and existing demo APIs keep working. If Redis or NATS is configured but unavailable, requests and smoke paths fall back without hard failing.

`33-03` does not move OCR, parser, indexing or eval model execution into a production async queue. The worker skeleton only publishes / consumes demo messages and updates task status.

### Redis Responsibilities

| Responsibility | API-facing meaning | Boundary |
|---|---|---|
| Session cache | Future formal auth session / refresh metadata cache. | Not a password store, identity provider or RBAC source of truth. |
| Query cache | Short TTL cache for project-scoped RAG query results or retrieval candidates. | Cache keys must include organization / project / role / provider config. |
| Rate limit | Per user / organization / IP / API group counters. | Not an audit log or permission check replacement. |
| Worker lock | Idempotency lock for OCR / parser / index / eval tasks. | TTL required; not long-term task status. |
| Short-term chat history | Ephemeral chat context for future UI continuity. | Not canonical citations, document chunks, Agent run history or eval result storage. |

### Redis Runtime Slice

| API surface | Redis use | Fallback |
|---|---|---|
| `GET /health` | Returns `redis=disabled`, `redis=ok` or `redis=unavailable`. | Service health stays `ok`; unavailable detail is informational. |
| `POST /auth/login` | Best-effort stores a hashed bearer token session payload with short TTL. | Login still succeeds; signed token remains the source of auth. |
| `POST /rag/query` | Applies simple Redis counter rate limit and reads / writes short TTL query cache. | Query still runs when Redis is disabled or unavailable; trace metadata records cache / rate-limit status when Redis is configured. |

Redis query cache keys include auth mode, role, organization / project access, provider settings and the visible document / chunk signature. Cache entries must not be shared across projects or roles.

The Redis Python client is optional. Install the backend with `.[dev,redis]`, or build Docker with `DOCURAG_INSTALL_REDIS=true`, before expecting `DOCURAG_REDIS_URL` to connect to a real Redis service. Without that client, `/health` reports `redis=unavailable` and existing APIs keep their fallback path.

### NATS Worker Skeleton

| Surface | Behavior | Fallback |
|---|---|---|
| `NatsRuntime.publish` / `subscribe` | Publishes JSON payloads and dispatches subscribed handlers. `memory://` is supported for smoke validation. | Returns `disabled` or `unavailable` instead of raising when runtime is missing. |
| `WorkerSkeleton` | Subscribes to OCR, parser, indexing and eval topics, then marks placeholder task handlers as `running` -> `succeeded`. | Failed publish marks the task `failed` with `error_code=nats_unavailable`. |
| `scripts/nats-worker-smoke.ps1` | Runs an in-memory publish / consume / task status smoke check. | Does not require a real NATS server. |

The optional real NATS client is in `backend[nats]`. Docker Compose includes a `nats` profile, but the default backend image does not install the client unless `DOCURAG_INSTALL_NATS=true` is set.

### NATS / JetStream Topics

| Topic | Trigger | Payload keys |
|---|---|---|
| `document.uploaded` | Upload API saves document metadata. | `event_id`, `document_id`, `organization_id`, `project_id`, `actor_user_id`, `source_type`, `trace_id` |
| `document.ocr.requested` | API or dispatcher requests OCR. | `task_id`, `document_id`, `provider`, `idempotency_key`, `attempt`, `trace_id` |
| `document.parse.requested` | API or OCR completion requests parser. | `task_id`, `document_id`, `parser_source`, `idempotency_key`, `attempt`, `trace_id` |
| `document.index.requested` | API or parser completion requests indexing. | `task_id`, `document_id`, `chunk_source_version`, `idempotency_key`, `attempt`, `trace_id` |
| `rag.eval.requested` | Admin / Analyst requests built-in eval. | `task_id`, `eval_run_id`, `dataset_id`, `strategy`, `project_id`, `idempotency_key` |

Event payloads must not include file bytes, raw OCR text, secrets, API keys or cross-project data. Workers must fetch canonical data by id and re-check project access / task authorization through backend policy.

### Task Status Schema

```json
{
  "task_id": "task_123",
  "task_type": "ocr",
  "status": "queued",
  "organization_id": "org_demo",
  "project_id": "project_demo",
  "document_id": "doc_123",
  "eval_run_id": null,
  "idempotency_key": "ocr:project_demo:doc_123:source_v1",
  "attempt": 1,
  "max_attempts": 3,
  "created_at": "2026-06-07T14:30:00Z",
  "started_at": null,
  "updated_at": "2026-06-07T14:30:00Z",
  "finished_at": null,
  "failure_reason": null,
  "error_code": null,
  "trace_metadata": {
    "trace_id": "trace_123"
  }
}
```

Allowed task statuses are `queued`, `running`, `retrying`, `succeeded`, `failed` and `cancelled`.

Task status endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tasks` | Lists stored worker task records. Formal auth mode filters by accessible project ids. |
| `GET` | `/tasks/{task_id}` | Returns one worker task record; formal auth mode denies cross-project access. |

Retry policy:

- Retry transient failures such as `provider_unavailable`, `qdrant_unavailable`, `rate_limited` and `worker_lock_conflict` with exponential backoff and jitter.
- Do not retry terminal failures such as `permission_denied`, `project_access_denied`, `unsupported_file`, `invalid_input`, `unsafe_path` or `schema_validation_failed`.
- Retries must keep the same `idempotency_key`, increment `attempt` and preserve `trace_id`.

Idempotency key policy:

- Use deterministic keys such as `{task_type}:{project_id}:{resource_id}:{source_version}:{request_fingerprint}`.
- Replayed events with the same key must not duplicate OCR results, parser fields, vector points, eval runs or Agent traces.
- A new source version, parser policy or indexing strategy must produce a new key.

## Projects

| Method | Endpoint | Description |
|---|---|---|
| GET | `/projects` | List visible projects |
| POST | `/projects` | Create project |
| GET | `/projects/{project_id}` | Project detail |

## Documents

| Method | Endpoint | Description |
|---|---|---|
| GET | `/projects/{project_id}/documents` | List documents |
| POST | `/projects/{project_id}/documents` | Create document metadata |
| GET | `/documents/{document_id}` | Document detail |
| GET | `/documents/{document_id}/pages` | OCR page text |
| GET | `/documents/{document_id}/fields` | Extracted fields |
| POST | `/documents/{document_id}/parse` | Run the MVP parser for an OCR-completed, direct text, or text-native PDF document |
| GET | `/documents/{document_id}/chunks` | Document chunks |
| POST | `/documents/{document_id}/index/vector` | Index document chunks into Qdrant when embedding / Qdrant runtime is available; frontend v0.27.0 calls this best-effort after OCR |

## Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/projects/{project_id}/chat` | Ask a demo RAG question |

## Agent

| Method | Endpoint | Description |
|---|---|---|
| POST | `/agent/run` | Phase 25 deterministic Agent run endpoint |
| GET | `/agent/runs/{run_id}` | Phase 25 Agent run lookup endpoint |

## Eval

| Method | Endpoint | Description |
|---|---|---|
| GET | `/projects/{project_id}/eval-runs` | List sample eval metrics |
| POST | `/eval/rag/built-in` | v0.29.0 built-in RAG benchmark for Admin / Analyst; fixed `hybrid_rerank`, synthetic Chinese invoice fixtures |
| POST | `/eval/runs` | v0.36.0 managed dataset strategy comparison run for Admin / Analyst |
| GET | `/eval/runs/{run_id}` | v0.36.0 strategy comparison summary lookup |
| GET | `/eval/runs/{run_id}/items` | v0.36.0 failure cases, fallback cases and rerank analysis rows |

## Phase 36 Eval Run API

`POST /eval/runs` runs a managed eval dataset against selected retrieval strategies. Request body:

```json
{
  "dataset_id": "eval_dataset_123",
  "strategies": ["keyword", "hybrid_rerank", "vector"],
  "top_k": 5
}
```

Allowed strategies are `keyword`, `vector`, `vector_rerank`, `hybrid` and `hybrid_rerank`. The endpoint stores the eval run result and returns a compact strategy comparison summary:

- `strategy_summaries`: one row per strategy with Hit Rate@K, MRR@K, Recall@K, average latency, failure count, fallback count, trace metadata count and fallback reasons.
- `strategies`: the de-duplicated strategy config used by the run.
- `dataset_name`, `top_k`, `created_at` and `run_id`: UI display and lookup metadata.

`GET /eval/runs/{run_id}` returns the persisted summary. `GET /eval/runs/{run_id}/items` returns detail rows for:

- `failed_cases`: queries with no hit or runtime error.
- `fallback_cases`: queries with explicit fallback metadata, for example vector or rerank runtime unavailable.
- `rerank_analysis`: before / after ranking and rerank score rows for `vector_rerank` or `hybrid_rerank`, including `pre_rerank_rank`, `post_rerank_rank`, `pre_rerank_score`, `rerank_score`, `rerank_status` and `fallback_state`.

When embedding, Qdrant or reranker runtime is unavailable, vector-backed strategies are represented with explicit failure / fallback rows instead of crashing the whole strategy comparison. This API does not change the default retrieval provider, does not tune the rerank model, and is not LLM-as-judge, answer faithfulness scoring, citation quality scoring or production monitoring trend storage.

## Phase 37 Inference Provider Ops Contract

`37-01` was a Markdown-only contract ticket. It defines how LLM / VLM inference providers should report selection, latency, token usage and fallback state. `37-02` adds the first OpenAI-compatible LLM adapter for RAG generation while keeping Ollama as the default local fallback path. `37-03` adds local vLLM serving docs and benchmark smoke for an OpenAI-compatible endpoint, but does not make vLLM the only runtime or claim production inference serving.

### Provider Boundary

| Provider label | HTTP shape | Intended use | Boundary |
|---|---|---|---|
| `ollama` | Ollama `/api/generate` and embedding endpoints | Current local demo LLM / VLM path and fallback baseline. | Must remain available as a local fallback path; no production SLA claim. |
| `openai_compatible` | OpenAI-compatible chat endpoint, configured by base URL and model. | Implemented in `37-02` for RAG generation against hosted or local compatible servers. | Requires explicit env selection and must not require a production secret for local validation. |
| `vllm` | OpenAI-compatible endpoint served by vLLM. | Optional local serving / benchmark path documented in `37-03`. | Uses the same `openai_compatible` backend adapter; no production SLA, model registry, autoscaling or multi-GPU serving claim. |

Provider selection must be explicit in trace metadata:

```json
{
  "inference_provider": "ollama",
  "inference_endpoint_kind": "ollama_generate",
  "inference_model": "qwen3.5:4b",
  "provider_fallback_chain": ["ollama"],
  "provider_status": "ok"
}
```

`37-02` exposes `DOCURAG_LLM_PROVIDER=ollama|openai_compatible` for RAG answer generation. `openai_compatible` uses `DOCURAG_LLM_BASE_URL` as the endpoint root, `DOCURAG_LLM_MODEL` as the model name, `DOCURAG_LLM_TIMEOUT_SECONDS` as the request timeout and optional `DOCURAG_LLM_API_KEY` as a bearer token. Local compatible servers that do not require auth can leave `DOCURAG_LLM_API_KEY` empty. `DOCURAG_VLM_PROVIDER` behavior remains unchanged in `37-02`; OpenAI-compatible VLM parsing is not added by this ticket.

### Metrics Contract

Every provider response should normalize inference metrics into trace metadata when the provider supplies or can estimate them:

| Field | Meaning |
|---|---|
| `prompt_tokens` | Input token count reported by provider or estimator. |
| `completion_tokens` | Generated token count reported by provider or estimator. |
| `total_tokens` | Prompt + completion token total. |
| `latency_ms` | Wall-clock request latency. |
| `tokens_per_second` | Completion throughput when completion token count is known. |
| `finish_reason` | Provider stop reason such as `stop`, `length`, `timeout` or `error`. |
| `gpu_memory_estimate_mb` | Optional local serving estimate, not a measured production value unless explicitly measured by a later benchmark ticket. |
| `kv_cache_estimate_mb` | Optional KV cache estimate based on model, context length, batch size and dtype. |
| `provider_request_id` | Provider request id when available; must not include API keys or secrets. |

Metrics may be `null` when unavailable, but missing metrics must not be silently presented as zero. UI and smoke reports should distinguish measured values from estimates.

### Fallback And Failure Contract

| Condition | Required behavior |
|---|---|
| Provider disabled or unavailable | Preserve the existing fallback path and set `provider_status=unavailable` with a clear `fallback_reason`. |
| Timeout | Stop waiting at the configured timeout, set `finish_reason=timeout`, and fall back without corrupting saved OCR, parser, RAG or Agent data. |
| Malformed response | Set `provider_status=malformed_response`, keep the raw provider payload out of user-facing UI unless explicitly requested, and fall back to the previous safe path. |
| Rate limited or overloaded | Record `provider_status=rate_limited` or `overloaded`; retry only when a later ticket defines retry policy. |
| Unsupported modality | VLM parser must fall back to existing deterministic parser behavior; RAG generation must fall back to retrieved chunks / deterministic answer path. |

Fallback metadata belongs in response trace metadata and persisted run metadata where that feature already persists traces. It must not alter permission checks, project filtering, Agent tool allowlists, parser schema or retrieval ranking.

### Validation Boundary

`37-02` validates the OpenAI-compatible LLM adapter with backend tests for success, timeout, malformed response and unavailable endpoint handling. It does not add an OpenAI SDK dependency, paid API key handling, streaming API, VLM parser runtime change, Agent planner change or production inference gateway.

`37-03` validates the local vLLM serving path with `scripts/inference-benchmark-smoke.ps1`. The smoke script calls an OpenAI-compatible `/v1/chat/completions` endpoint when available and writes latency, token, throughput, KV cache estimate and GPU memory estimate into a local JSON report. If the endpoint is unavailable, it writes `status=skipped`, `provider_status=unavailable`, skip reason and fallback guidance to Ollama or deterministic baseline.

### 37-02 Runtime Notes

- `OpenAiCompatibleLlmProvider` calls `{DOCURAG_LLM_BASE_URL}/chat/completions` with non-streaming chat completion payloads.
- The adapter normalizes prompt tokens, completion tokens, total tokens, finish reason, provider request id, provider latency and tokens per second into the existing RAG trace metadata when the provider returns those fields.
- Timeout, connection failure and malformed response raise provider errors; `/rag/query` keeps the existing provider fallback path and returns retrieved chunks with `llm_fallback_reason=provider_error`.
- Ollama remains the default `DOCURAG_LLM_PROVIDER=ollama` path and is not removed.

### 37-03 Local vLLM Notes

- vLLM local serving uses the same `DOCURAG_LLM_PROVIDER=openai_compatible`, `DOCURAG_LLM_BASE_URL`, `DOCURAG_LLM_MODEL`, `DOCURAG_LLM_TIMEOUT_SECONDS` and optional `DOCURAG_LLM_API_KEY` settings.
- `docs/LOCAL_DEV_SETUP.md` documents the vLLM Docker path and hardware constraints; Windows native vLLM startup is not assumed.
- `scripts/inference-benchmark-smoke.ps1` writes measured latency and token fields only when the endpoint responds; KV cache and GPU memory fields remain estimates.
- `37-03` does not change RAG prompts, VLM parser prompts, Agent planner behavior or retrieval ranking.

## Phase 29 Built-in RAG Eval Contract

`POST /eval/rag/built-in` wraps the existing retrieval eval runner for the backend admin surface. It is intentionally narrow:

- Strategy is always `hybrid_rerank`; the endpoint does not accept a strategy selector.
- Dataset is always `sample-data/eval/built-in-rag-eval-zh-invoices.json`.
- The fixture set contains 10 demo-safe synthetic Chinese invoices: `NVDLA` 1, `GOOGLE` 1, `OpenAI` 1, `Intel` 3 and `DocuRAG` 4. Dates and TWD amounts are unique.
- Response summary only exposes `hit_rate_at_k`, `mrr_at_k`, `average_latency_ms`, `failure_count` and `fallback_count` for the first admin UI slice.
- `failed_cases` and `fallback_cases` are available for collapsible UI details, not a full dashboard or ranking table.
- If embedding, Qdrant or reranker runtime is unavailable, the endpoint falls back to keyword evidence with explicit fallback metadata.
- Demo auth mode uses the same ingestion write guard: Admin / Analyst may run it; Viewer receives 403.

This endpoint is not production eval history, custom dataset upload, OCR accuracy evaluation, VLM parser evaluation, LLM-as-judge, answer faithfulness scoring or citation quality scoring.

## Phase 28 Document Source Router Contract

`28-01` 固定 upload 後的 source router 與 normalized document text contract；`28-02` / `28-03` 已分別補上 `.txt` direct ingestion 與 text-native PDF extraction；`28-04` 補上 demo auth mode 與 role guard。v0.28.0 runtime 不應把 `.txt`、PDF、OCR 與 VLM fields 混在同一路徑。

### Source Router

| Router target | Detection input | Runtime meaning | Notes |
|---|---|---|---|
| `image_ocr` | image file type or image content type | 走既有 provider-selected OCR，產生 OCR text / OCR lines / chunks。 | `ocr_mock` 只作手動 fallback / validation path，不是正式來源。 |
| `text_upload` | `.txt` | 直接讀 UTF-8 原文、做基本空白 normalization 並建立 chunks。 | Current runtime；不需要 OCR job，也不標示為 OCR completed。 |
| `pdf_text` | PDF with extractable text layer | 使用 `pypdf` 抽取 text-native PDF 文字並建立 chunks。 | 保留 `page_number`；`bbox` 可為 `null`，不可假造座標。 |
| `pdf_scanned_pending_ocr` | PDF without extractable text or future scanned detection | `34-02` 會 render page images；`34-03` 可透過 provider-selected OCR 處理 page images。 | Page OCR 成功後會建立 `pdf_page_ocr` chunks；仍不是 production layout / table reconstruction。 |

### Normalized Document Text

後續 source router 輸出應整理成同一個 chunk input contract，讓 RAG、Qdrant payload 與 Agent citations 不依賴單一路徑：

```json
{
  "document_id": "doc_123",
  "source_type": "text_upload",
  "text": "Payment terms: Net 15",
  "page_number": null,
  "bbox": null,
  "confidence": null,
  "metadata": {
    "filename": "invoice.txt",
    "content_source": "text_upload",
    "origin": "uploaded_text",
    "project_id": null,
    "tenant_id": null
  },
  "created_at": "2026-05-25T10:00:00Z"
}
```

Frontend ingestion flow 依 source type 顯示不同狀態：`text_upload` 可直接建立知識庫並接 best-effort parser / vector indexing，`image_ocr` 先 OCR，`pdf_text` 顯示 text-native PDF extraction ready，`pdf_scanned_pending_ocr` / `pdf_mixed_pending_ocr` 可透過 API document detail 看到 page images 的 OCR result 或 failure。

`28-03` 新增的 PDF dependency 僅限 `pypdf` text extraction；仍不新增 PDF rendering、多頁 OCR pipeline、worker、DB schema、正式 auth / RBAC、Redis、NATS 或 deployment 設定。

## Phase 34 Scanned PDF OCR Contract

`34-01` 定義 contract；`34-02` 新增 demo-safe PDF page image rendering；`34-03` 將 provider-selected OCR 接到 scanned / mixed PDF page images，沿用這裡的 source routing、page image、OCR block、page-level status、retry 與 failure reason contract。

### PDF Source Routing

| PDF class | Detection rule | Contract source | Runtime behavior |
|---|---|---|---|
| Text-native PDF | Every required page has extractable text. | `pdf_text` | Current runtime uses `pypdf` extraction and creates page-aware chunks. |
| Scanned PDF | No useful text layer, pages require rendering. | `pdf_scanned_pending_ocr` | `34-02` renders bounded PNG page images; `34-03` runs provider-selected page-level OCR and creates `pdf_page_ocr` chunks. |
| Mixed PDF | Some pages have text, some pages require OCR. | `pdf_mixed_pending_ocr` | Text pages produce `pdf_text` chunks; scanned pages render `pdf_mixed_pending_ocr` page images, then OCR appends `pdf_page_ocr` chunks. |
| Invalid PDF | Parser cannot open, encrypted without key, corrupt, unsupported, or too large. | `pdf_invalid` | No chunks are created; document stores a clear failure reason. |

Current runtime can render scanned / mixed PDF page images and run provider-selected OCR on those page images. It still must not claim production layout analysis, table reconstruction, human correction or async worker durability.

### Page Image Contract

`34-02` stores page image records on document metadata:

```json
{
  "image_id": "doc_123-page-001",
  "document_id": "doc_123",
  "page_number": 1,
  "path": "page-images/doc_123/page-001.png",
  "width": 1275,
  "height": 1650,
  "dpi": 150,
  "checksum": "64-character-sha256-hex",
  "page_status": "rendered",
  "source_type": "pdf_scanned_pending_ocr",
  "ocr_text": "",
  "ocr_blocks": [],
  "ocr_attempts": 0,
  "ocr_provider": null,
  "failure_reason": null,
  "metadata": {},
  "created_at": "2026-06-07T10:00:00Z",
  "updated_at": null
}
```

`34-02` writes `rendered` records after page image rendering. `34-03` may update page records to `ocr_running`, `ocr_succeeded` or `ocr_failed`; the schema also reserves `ocr_queued` and `ocr_retrying` for future worker-backed execution. Text-native pages in a mixed PDF keep `pdf_text` chunks as the source of truth and are not rendered.

### OCR Block Contract

Each OCR page result must preserve block-level evidence:

```json
{
  "document_id": "doc_123",
  "page_number": 1,
  "status": "ocr_succeeded",
  "blocks": [
    {
      "block_id": "doc_123_p001_b001",
      "text": "Payment terms: Net 15",
      "bbox": {
        "x_min": 120,
        "y_min": 240,
        "x_max": 720,
        "y_max": 282
      },
      "confidence": 0.96,
      "reading_order": 1,
      "provider": "paddleocr",
      "language": "ch"
    }
  ],
  "metadata": {
    "attempt": 1,
    "provider_version": "PP-OCRv4",
    "duration_ms": 860
  }
}
```

OCR blocks are the evidence source for future scanned PDF chunks, parser context and citations. If `bbox` or `confidence` is unavailable, the value must be `null`; the runtime must not invent coordinates or scores.

### Retry and Failure Reason

Retry state is page-level:

```json
{
  "page_number": 2,
  "page_status": "ocr_retrying",
  "attempt": 2,
  "max_attempts": 3,
  "last_failure_reason": "ocr_timeout",
  "next_retry_at": "2026-06-07T10:05:00Z"
}
```

Allowed failure reasons include `pdf_invalid`, `pdf_encrypted`, `pdf_render_failed`, `page_image_too_large`, `ocr_provider_unavailable`, `ocr_timeout`, `ocr_invalid_output`, `page_empty`, `worker_unavailable` and `unknown_error`. Document-level status is `ready` only when all required pages are either `ocr_succeeded` or intentionally `skipped_text_native`.

### Handoff to Parser, Chunks, Indexing and Worker Status

- Parser receives compact OCR text plus OCR blocks after required pages finish; mixed PDFs may combine `pdf_text` text pages and OCR blocks from scanned pages.
- Chunks created from scanned pages must keep `source_type=pdf_page_ocr`, `content_source=pdf_scanned_ocr`, `page_number`, block ids, bbox and confidence where available.
- Current `34-03` runtime exposes this through `POST /documents/{document_id}/ocr` and persisted document detail: successful scanned pages become `ocr_succeeded`, failed pages become `ocr_failed`, and retry increments `ocr_attempts` without duplicating old `pdf_page_ocr` chunks.
- Vector indexing must wait for page-level OCR completion or explicitly record partial / skipped pages in metadata.
- Worker task status from Phase 33 should mirror document and page progress: rendering tasks can publish `document.ocr.requested`; OCR tasks update queued / running / retrying / succeeded / failed without changing OCR model behavior in this contract ticket.

This contract and runtime slice do not implement production table reconstruction, layout analysis, human correction workflow, OCR accuracy tuning, VLM parser changes, RAG ranking changes, Agent planner changes or eval dashboard changes.

## Phase 24 Parser Contract Draft

## Phase 27 Vector Source Contract

`27-03` 只固定 normalized text source 與 vector source 邊界，不新增 runtime。現有 `POST /documents/{document_id}/index/vector` 仍讀取文件已保存的 chunks；v0.28.0 runtime 已讓 `text_upload` 與 `pdf_text` 也能成為索引來源。

### Source Taxonomy

| Source type | Content source | Runtime status | Notes |
|---|---|---|---|
| `ocr_image` | OCR text / OCR lines from image upload | Current demo path | 圖片或掃描類文件先走 OCR，再用 OCR chunks 寫入 Qdrant。 |
| `text_upload` | Original text file body | Current runtime | `.txt` 直接建立 chunks，不需要假裝經過 OCR。 |
| `pdf_text` | Text-native PDF extraction | Current runtime | 只代表 PDF 內已有文字層；不包含 scanned PDF。 |
| `pdf_scanned_pending_ocr` | Rendered PDF page images pending OCR | Current rendering path | `34-02` 可產生 page images；page image metadata 會記錄後續 OCR status。 |
| `pdf_page_ocr` | OCR-derived scanned PDF page chunks | Current page OCR path | `34-03` 成功後產生，可保留 `content_source=pdf_scanned_ocr`、page number、bbox / confidence 與 page image metadata；不代表 production layout / table understanding。 |

### Normalized Text Source

後續 ingestion source router 應把各來源整理成同一個 chunk input contract：

```json
{
  "document_id": "doc_123",
  "filename": "invoice.png",
  "source_type": "ocr_image",
  "content_source": "ocr_image",
  "chunk_id": "chunk_001",
  "text": "Payment terms: Net 15",
  "page_number": 1,
  "bbox": {
    "x_min": 10,
    "y_min": 20,
    "x_max": 260,
    "y_max": 44
  },
  "confidence": 0.96,
  "metadata": {
    "project_id": null,
    "tenant_id": null
  }
}
```

Qdrant payload 至少保留 `document_id`、`filename`、`chunk_id`、`source_type`、`content_source`、`page_number`、`created_at` 與 future `project_id` / `tenant_id` 欄位位置。`bbox` 與 `confidence` 對 `text_upload` / `pdf_text` 可為 `null`；對 `ocr_image` 則應沿用 OCR line trace。

## Phase 35 Indexing Quality API Contract

`35-01` 先定義 API contract。`35-02` 已在既有 `POST /documents/{document_id}/index/vector` 上加入可選 `chunking_strategy` request body，支援 `fixed_size` 與 `semantic`。`35-03` 已補上 Qdrant payload index 建立、tenant / project / document / source filter、document stale vector cleanup，以及 project-scope reindex API；仍不新增 worker job、eval dashboard、rerank algorithm、embedding model selection、LLM generation 或新的 permission guard。

### Chunking Request Boundary

Current `35-02` vector indexing requests may accept:

```json
{
  "chunking_strategy": "semantic",
  "cleanup_stale": true
}
```

No request body defaults to `fixed_size` and `cleanup_stale=false`, preserving the existing demo flow. `fixed_size` is the deterministic baseline and splits stored source chunks into bounded char windows when needed. `semantic` uses paragraph / section boundaries already present in stored chunk text, then falls back to fixed windows with `chunking_fallback_reason=semantic_boundaries_unavailable` when boundaries are unclear. `35-02` does not implement `parent_child` runtime and does not use LLM-based semantic segmentation.

`VectorIndexingResponse` now exposes `chunking_strategy`, `chunking_version`, `payload_index_status`, `payload_index_fields` and `stale_cleanup_status`. Indexed chunk payload metadata includes `chunking_strategy`, `chunking_version`, `chunk_index`, `char_count`, `token_count`, `source_type`, `source_chunk_id`, `chunk_part_index`, `project_id`, `tenant_id`, `content_source`, `chunk_type` and `page_number` when available.

Future vector indexing requests may add `force_reindex`, `reason` or `parent_child`, but those remain outside `35-03`.

### Qdrant Payload Contract

Qdrant payload metadata must support filtering by tenant, project, document, source, page and chunk type:

```json
{
  "tenant_id": "tenant_demo",
  "project_id": "project_demo",
  "document_id": "doc_123",
  "filename": "invoice.pdf",
  "source_type": "pdf_page_ocr",
  "content_source": "pdf_scanned_ocr",
  "page_number": 1,
  "chunk_id": "doc_123:pdf_page_ocr:1:0001",
  "chunk_type": "child",
  "chunking_strategy": "parent_child",
  "chunking_version": "v1",
  "parent_chunk_id": "doc_123:parent:1",
  "index_run_id": "idx_20260607_001",
  "document_revision": "rev_3",
  "created_at": "2026-06-07T00:00:00Z",
  "indexed_at": "2026-06-07T00:00:00Z",
  "stale_at": null
}
```

Retrieval requests must apply tenant / project filters before narrowing to document, source, page or chunk type filters. API permission remains controlled by Auth / RBAC guards; Qdrant payload filters are the retrieval boundary that prevents cross-tenant, cross-project or cross-document leakage after a user is authorized.

### Reindex and Stale Vector Cleanup

`35-03` keeps document-level reindex on the existing `POST /documents/{document_id}/index/vector` endpoint by using `cleanup_stale=true`. It also adds `POST /documents/index/vector/reindex` for project-scope reindex. The project request accepts optional `project_id`, `chunking_strategy` and `cleanup_stale`; formal auth defaults to the active project when `project_id` is omitted. The response exposes target project, status, document count and completed / skipped / failed counts plus per-document `VectorIndexingResponse` results.

Stale vector cleanup identifies older Qdrant points by tenant / project / document scope and deletes only points for the same document that are not part of the latest successful point id set. Cleanup must not delete document metadata, OCR output, parser fields or source chunks.

## Phase 36 Eval Dashboard / Rerank Analysis Contract

`36-01` is a Markdown-only contract ticket. It defines the future evaluation dashboard and rerank analysis shape on top of the existing retrieval eval runner and built-in RAG benchmark. It does not add runtime endpoints, frontend UI, dataset persistence, LLM-as-judge, answer faithfulness scoring, citation quality scoring, OCR eval or ranking algorithm changes.

### Phase 36 Runtime API Surface

The built-in benchmark remains `POST /eval/rag/built-in`. `36-02` adds controlled eval dataset / eval item management for Admin / Analyst. `36-03` adds managed eval run strategy comparison and persisted run lookup for Admin / Analyst.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/eval/datasets` | List eval datasets visible to the active project. |
| POST | `/eval/datasets` | Create a demo-safe eval dataset. |
| GET | `/eval/datasets/{dataset_id}` | Read dataset metadata and current eval items. |
| PATCH | `/eval/datasets/{dataset_id}` | Update dataset name / description. |
| DELETE | `/eval/datasets/{dataset_id}` | Delete one dataset and its eval items. |
| GET | `/eval/datasets/{dataset_id}/items` | List eval items in a dataset. |
| POST | `/eval/datasets/{dataset_id}/items` | Create an eval item. |
| GET | `/eval/datasets/{dataset_id}/items/{item_id}` | Read one eval item. |
| PATCH | `/eval/datasets/{dataset_id}/items/{item_id}` | Update query, expected terms, expected ids, tags or notes. |
| DELETE | `/eval/datasets/{dataset_id}/items/{item_id}` | Delete one eval item. |
| POST | `/eval/runs` | Future `36-03`: run one or more retrieval strategies against a dataset. |
| GET | `/eval/runs/{run_id}` | Future `36-03`: read run summary, environment and strategy metrics. |
| GET | `/eval/runs/{run_id}/items` | Future `36-03`: read failed / fallback / selected case details. |

`36-02` endpoints reuse the existing ingestion guard. Admin / Analyst can create, update and delete eval datasets / items. Viewer receives `403 forbidden` in demo / formal auth mode and cannot manage datasets. Formal auth datasets are project-scoped to the active project; cross-project dataset access returns generic `403 forbidden`.

### Data Shapes

`EvalDataset`:

```json
{
  "dataset_id": "invoice_quality_v1",
  "name": "Invoice retrieval quality v1",
  "description": "Demo-safe retrieval cases for invoice evidence.",
  "project_id": "project_demo",
  "item_count": 12,
  "schema_version": "eval_dataset_v1",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z"
}
```

`EvalItem`:

```json
{
  "item_id": "invoice_due_date_001",
  "dataset_id": "invoice_quality_v1",
  "project_id": "project_demo",
  "query": "付款期限是什麼？",
  "expected_document_ids": ["doc_aurora"],
  "expected_chunk_ids": ["doc_aurora:chunk:payment_terms"],
  "expected_terms": ["Net 15"],
  "tags": ["invoice", "payment_terms", "zh_tw"],
  "notes": "Demo-safe invoice evidence case.",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z"
}
```

`EvalRunSummary`:

```json
{
  "run_id": "eval_run_001",
  "dataset_id": "invoice_quality_v1",
  "status": "completed",
  "strategies": ["keyword", "vector", "hybrid", "vector_rerank", "hybrid_rerank"],
  "metrics": {
    "hybrid_rerank": {
      "hit_rate_at_k": 0.83,
      "mrr_at_k": 0.71,
      "recall_at_k": 0.79,
      "precision_at_k": 0.42,
      "average_latency_ms": 118.4,
      "failure_count": 1,
      "fallback_count": 2
    }
  }
}
```

### Metrics Contract

| Metric | Contract |
|---|---|
| `hit_rate_at_k` | Fraction of cases where at least one expected document or chunk appears in top K. |
| `mrr_at_k` | Mean reciprocal rank of the first expected hit within top K. |
| `recall_at_k` | Fraction of expected evidence ids found in top K. |
| `precision_at_k` | Fraction of retrieved top K items that match expected evidence ids. |
| `average_latency_ms` | Average end-to-end retrieval latency for the strategy, excluding UI render time. |
| `failure_count` | Cases with no expected hit or runtime error that prevents evaluation. |
| `fallback_count` | Cases that completed with fallback metadata, such as vector unavailable or reranker unavailable. |

### Case And Rerank Analysis

Dashboard case detail rows should expose:

- `case_id`, `query`, `tags`, `top_k`, `status`, `strategy`, `latency_ms`.
- Retrieved candidates with `rank`, `document_id`, `chunk_id`, `score`, `source_type`, `page_number`, `trace_metadata`.
- `expected_hit` and `matched_expected_ids`.
- `failure_reasons` and `fallback_reasons`, both as arrays so multiple conditions can be shown without losing detail.

Rerank analysis rows should expose:

- `pre_rerank_rank`, `post_rerank_rank`, `pre_rerank_score`, `rerank_score`.
- `final_score_source`, such as `rerank_score`, `hybrid_score`, `vector_score` or `keyword_score`.
- `rerank_provider`, `rerank_model`, `rerank_status`, `rerank_latency_ms`.
- `trace_metadata_coverage`, counting how many returned candidates include strategy, source, fallback and score metadata.

UI contract for Phase 36 should stay operational and compact: summary metric cards, strategy comparison table, failure / fallback case lists, and a rerank analysis table. It must not display answer faithfulness, citation quality scoring or LLM-as-judge output unless a later ticket explicitly adds those features.

VLM structured fields 不在本 ticket 自動寫入 retrieval chunks；若後續要把欄位索引進 Qdrant，必須另開 ticket 定義 field-indexing policy、dedupe key 與 citation semantics。

Phase 24 的 parser contract 先支援 invoice MVP。`24-01` 固定文件與 API 草案，`24-02` 新增 deterministic parser service，`24-03` 新增 parse / fields API 與 local JSON persistence。此 contract 是 VLM-compatible，不代表目前已接真正 VLM、LLM parser、DB、worker 或 production parser pipeline。

### Parser Sources

| Source | Scope |
|---|---|
| `deterministic_invoice` | Phase 24 MVP fallback。只從既有 OCR text / OCR lines 做 demo-safe 規則抽取，不新增外部依賴。 |
| `llm_invoice` | Future text-only parser。只使用 OCR text / lines，不直接讀圖片。 |
| `vlm_invoice` | Future VLM parser。可使用原始圖片 / layout trace，但不屬於 `24-01` 或 deterministic MVP runtime。 |

### Status Contract

Parser 狀態存在於 `ParserResult.status`；`24-03` 起 document processing metadata 也包含 `processing.parser` step。Parser failure 不應清空 OCR result、chunks 或影響 Viewer Chat 的 default RAG path。

| Status | Meaning |
|---|---|
| `pending` | 尚未執行 parser，或沒有已保存的 structured fields。 |
| `parsing` | Parser request 已開始；同步 MVP 通常只在 request lifecycle 內短暫出現。 |
| `parsed` | Parser 完成，`fields` 包含 structured fields 與 source trace。 |
| `failed` | Parser 失敗；`fallback_reason` 或 `error_message` 必須說明原因。 |

Document-level processing 後續以 `processing.parser=pending/running/completed/failed` 對應上述狀態；OCR 已完成但 parser 失敗時，`processing.ocr` 與 `processing.indexing` 保持原本狀態，`processing.failed_reason` 不應被 parser error 覆蓋，除非該 request 本身只回傳 parser failure。

### Schema Draft

`ExtractedField` 是欄位層級的最小 source trace 單位：

```json
{
  "value": "INV-2026-001",
  "confidence": 0.86,
  "source_text": "Invoice No: INV-2026-001",
  "source_page": 1,
  "source_bbox": {
    "x_min": 10,
    "y_min": 20,
    "x_max": 260,
    "y_max": 44
  },
  "parser_source": "deterministic_invoice",
  "fallback_reason": null
}
```

欄位規則：

- `confidence` 是 `0` 到 `1` 的 parser confidence；未知時可為 `null`，不可硬填假高分。
- `source_text` 必須來自 OCR text / OCR line / future VLM trace；無來源時可為 `null`，並用 `fallback_reason` 說明。
- `source_page` 與 `source_bbox` 延用 OCR line trace；OCR 沒提供時可為 `null`。
- `parser_source` 必須標明欄位來自 `deterministic_invoice`、`llm_invoice` 或 `vlm_invoice`。
- `fallback_reason` 只在欄位缺失、格式無法 normalization 或 parser fallback 時填入，例如 `field_not_found`、`ambiguous_currency`、`ocr_not_completed`。

`DocumentFields` 的 invoice MVP 欄位：

```json
{
  "document_type": { "value": "invoice" },
  "vendor_name": { "value": "Orion Office Supplies" },
  "invoice_number": { "value": "INV-2026-001" },
  "issue_date": { "value": "2026-05-24" },
  "total_amount": { "value": 1250.0 },
  "tax_amount": { "value": 62.5 },
  "currency": { "value": "USD" },
  "line_items": [
    {
      "description": { "value": "Notebook pack" },
      "quantity": { "value": 10 },
      "unit_price": { "value": 12.5 },
      "amount": { "value": 125.0 }
    }
  ]
}
```

完整 `ParserResult`：

```json
{
  "document_id": "doc_123",
  "status": "parsed",
  "parser_source": "deterministic_invoice",
  "schema_version": "invoice_fields_v1",
  "fields": {},
  "fallback_reason": null,
  "error_message": null,
  "source_ocr_status": "completed",
  "source_ocr_updated_at": "2026-05-24T10:00:00Z",
  "updated_at": "2026-05-24T10:00:01Z",
  "trace_metadata": {
    "input": "ocr_text",
    "parser_mode": "deterministic"
  }
}
```

### Endpoint Contract

`POST /documents/{document_id}/parse`

- Requires an existing document and completed OCR text.
- Request body is optional for MVP. If provided, `document_type` may be `invoice`. Phase 26 起 parser route defaults to VLM-first `vlm_invoice`; `DOCURAG_PARSER_SOURCE=deterministic_invoice` is only an explicit debug / validation override.
- Returns `ParserResult` and saves it to the document metadata JSON.
- `404` when document does not exist.
- `409` when OCR is not completed or OCR text is empty; response body should include `status=failed` and `fallback_reason=ocr_not_completed` or `empty_ocr_text`.
- Does not trigger OCR, vector indexing, RAG retrieval, Qdrant upsert, eval run or any async worker.

`GET /documents/{document_id}/fields`

- Returns saved `ParserResult` when parser has completed or failed.
- Returns `status=pending` when the document exists but no parser result has been saved yet.
- Does not trigger OCR, parser, vector indexing, RAG retrieval or any async worker.

`24-03` runtime notes：

- Parser result is stored on `DocumentMetadata.parser_result` in the existing local JSON metadata store.
- `ProcessingStatus.parser` uses `pending` / `completed` / `failed` to show parser state. Parser failure does not overwrite OCR / indexing state and does not affect Viewer Chat's default RAG path.
- `ProcessingJobType.PARSER` records the explicit parser request with success or failure metadata.

## Phase 25 Agent Tool-use Contract Draft

Phase 25 的 Agent MVP 只做 deterministic planner 與 allowlisted tool-use，用來把 Phase 24 structured fields、既有 document search / retrieval 與 deterministic invoice summary 串成可重播 trace。`25-03` 已新增 runtime API 與 local run persistence；frontend surface 與 demo smoke 由後續 tickets 實作。

此 contract 不代表 production autonomous Agent，不接 LLM planner、OpenAI function calling、Ollama planning call、任意 SQL、任意 tool execution、shell command、file system command、delete、reindex、DB、RBAC、worker、Redis 或 NATS。

### Agent Use Case

Phase 25 demo-safe 任務只支援 invoice / document question 類型，例如：

```text
整理這份 invoice 的結構化欄位，並用文件搜尋補充付款期限來源。
```

預期 trace：

1. 讀取既有 parser result。
2. 使用既有 document search 尋找來源片段。
3. 用 deterministic formatter 產生 invoice summary。
4. 回傳 final answer、citations 與 tool trace。

### Tool Allowlist

| Tool | Purpose | Input boundary | Output boundary |
|---|---|---|---|
| `get_document_fields` | 讀取 Phase 24 已保存的 `ParserResult` / `DocumentFields`。 | `document_id`，可選欄位名稱。 | structured fields、parser status、missing fields 與 source trace summary。 |
| `search_documents` | 使用既有 document search / keyword retrieval 查詢 chunks。 | demo-safe `query`、可選 `document_id`、可選 `top_k`。 | retrieved chunks、citations、retrieval source 與 trace metadata。 |
| `summarize_invoice_fields` | 將 invoice fields 與可用 citation 做 deterministic summary。 | `DocumentFields`、可選 retrieved chunks / citations。 | final answer draft、field summary、missing-field warnings。 |

Tool guardrails：

- Tool execution 必須是 read-only；不得執行 delete、reindex、shell、file system command、任意 HTTP call 或外部 side effect。
- 不提供任意 SQL 或 SQL template；`get_document_fields` 只讀 local JSON metadata 中已保存的 parser result。
- `search_documents` 不改變 RAG ranking、不觸發 vector indexing、不觸發 Qdrant upsert，也不改變 default Viewer Chat path。
- `summarize_invoice_fields` 不呼叫 LLM，不硬填缺失欄位；缺資料必須留在 observation / final answer warning。

### Deterministic Planner Boundary

Phase 25 planner 只能依 task keyword 與可用 `document_id` 產生固定步驟，不做 autonomous planning。

| Planner case | Plan |
|---|---|
| Invoice summary with `document_id` | `get_document_fields` -> `search_documents` -> `summarize_invoice_fields` |
| Document question with query only | `search_documents` -> final answer fallback |
| Missing OCR / parser fields | 記錄 failed / fallback step，不硬湊 structured answer。 |
| Unsupported task | 回傳 `failed` 或 `unsupported_task` observation，不嘗試任意 tool。 |

Future LLM planner 可在後續 phase 接入，但必須保留 allowlisted tools、read-only execution、explicit trace 與 permission boundary。Phase 25 不宣稱已完成 autonomous Agent 或 production AgentOps runtime。

### Schema Draft

`AgentStep` 描述 deterministic plan 中的預期步驟：

```json
{
  "step_id": "step_001",
  "order": 1,
  "title": "Read structured invoice fields",
  "tool_name": "get_document_fields",
  "status": "completed",
  "input_summary": "document_id=doc_123",
  "observation_summary": "Found parsed invoice fields.",
  "fallback_reason": null
}
```

`AgentToolCall` 描述實際 allowlisted tool execution：

```json
{
  "call_id": "call_001",
  "step_id": "step_001",
  "tool_name": "get_document_fields",
  "status": "completed",
  "input": {
    "document_id": "doc_123"
  },
  "output_summary": "invoice_number=INV-2026-001; total_amount=1250.0 USD",
  "observation": {
    "status": "completed",
    "message": "Parser result was available.",
    "missing_fields": []
  },
  "citations": [],
  "trace_metadata": {
    "tool_source": "local_metadata",
    "allowlisted": true,
    "read_only": true
  },
  "error_message": null
}
```

完整 `AgentRun`：

```json
{
  "run_id": "agent_run_123",
  "status": "completed",
  "task": "整理這份 invoice 並補充付款期限來源",
  "document_id": "doc_123",
  "query": "payment terms",
  "plan_steps": [],
  "tool_calls": [],
  "final_answer": {
    "text": "Invoice INV-2026-001 total is 1250.0 USD. Payment terms source: Net 15.",
    "status": "completed",
    "fallback_reason": null
  },
  "citations": [
    {
      "document_id": "doc_123",
      "filename": "invoice.txt",
      "chunk_id": "chunk_001",
      "text": "Payment terms: Net 15"
    }
  ],
  "trace": {
    "planner": "deterministic",
    "tool_policy": "allowlisted_read_only",
    "tool_count": 3,
    "fallback_count": 0
  },
  "created_at": "2026-05-24T10:00:00Z",
  "updated_at": "2026-05-24T10:00:01Z"
}
```

Status contract：

| Status | Meaning |
|---|---|
| `pending` | Run / step 已建立但尚未開始。同步 MVP 通常只在 request lifecycle 內短暫出現。 |
| `running` | Deterministic planner 或 tool execution 進行中。 |
| `completed` | 所有必要步驟完成，final answer 可用。 |
| `failed` | 必要資料缺失、unsupported task 或 allowlisted tool failure，需帶 `fallback_reason` / `error_message`。 |

### Endpoint Contract

`POST /agent/run`

- `25-03` runtime endpoint。
- Accepts demo-safe task, optional `document_id`, optional `query` and optional `top_k`.
- Uses deterministic planner only; it may call only `get_document_fields`, `search_documents` and `summarize_invoice_fields`.
- Returns `AgentRun` with `run_id`, `status`, `plan_steps`, `tool_calls`, `final_answer`, `citations`, `trace`, `created_at` and `updated_at`.
- Missing parser fields, search miss or unsupported task must be represented as failed / fallback steps.
- Must not execute arbitrary SQL, shell command, file system command, delete, reindex, arbitrary HTTP call or any non-allowlisted tool.

`GET /agent/runs/{run_id}`

- `25-03` runtime endpoint。
- Returns a saved `AgentRun` result when available.
- `404` when the run id does not exist.
- Does not re-run planner or tools.

`25-03` runtime notes：
- Agent run results are stored in the local JSON metadata store as `agent_runs.json`.
- Invoice summary runs with `document_id` execute `get_document_fields` -> `search_documents` -> `summarize_invoice_fields`.
- Query-only document question runs execute `search_documents` and return retrieved-chunk answer text with citations.
- Failed parser lookup, search miss or invalid document remains a saved `AgentRun` with failed / fallback plan steps.

## Phase 26 VLM Parser Provider Contract Draft

Phase 26 將 parser default 切成 VLM-first provider spike：`POST /documents/{document_id}/parse` 預設先嘗試 `vlm_invoice`，只有 VLM provider unavailable、timeout、unsupported file、invalid JSON、missing required fields 或 confidence too low 時，才 fallback 到 Phase 24 的 `deterministic_invoice`。這個 default-on 只代表 demo parser path 預設 VLM-first，不代表 production VLM parser、OpenAI SDK、streaming、function calling、PDF rendering、多頁 parser pipeline、worker、DB、RBAC 或 autonomous Agent。

### Provider Env Contract

| Env | Default | Meaning |
|---|---|---|
| `DOCURAG_VLM_PROVIDER` | `ollama` | Phase 26 parser provider selector。`ollama` 表示呼叫 Ollama-style local HTTP endpoint；`fake` 只供 demo smoke 驗證 success path；空字串可作 explicit disabled / fallback validation。 |
| `DOCURAG_VLM_BASE_URL` | `http://127.0.0.1:11434` | Local VLM endpoint base URL。 |
| `DOCURAG_VLM_MODEL` | `qwen3.5:4b` | Demo VLM parser model name；實際 production vision model selection 留給後續 phase。 |
| `DOCURAG_VLM_TIMEOUT_SECONDS` | `30` | VLM parser request timeout guardrail，避免 demo 卡死。 |
| `DOCURAG_VLM_MIN_CONFIDENCE` | `0.5` | Provider response confidence 低於門檻時 fallback 到 deterministic parser。 |
| `DOCURAG_PARSER_SOURCE` | `vlm_invoice` | Parser route override；預設 VLM-first，`deterministic_invoice` 只作 debug / validation override。 |

### Input Contract

Phase 26 VLM input resolver 只解析既有 upload metadata 與 `data/uploads/` 內的 demo-safe image file：

- 支援 `.png`、`.jpg` 與 `.jpeg`，並回傳 `document_id`、normalized file path、mime type、input source 與 fallback reason。
- 不支援 PDF rendering、multi-page image extraction、image preprocessing、deskew、layout detection 或 OCR accuracy tuning。
- Resolver 必須拒絕 missing file、unsupported file type、path traversal 或 upload root 以外的路徑，並回傳明確 failure reason。

### Output Contract

VLM provider 必須回傳 JSON object，並由 adapter 正規化成既有 Phase 24 schema，不新增平行欄位 schema。Ollama adapter 會優先讀取 `response`，若 `response` 為空則讀取 `thinking`；內容可以是純 JSON、markdown fenced JSON，或前後帶少量文字但包含第一個 JSON object 的 response：

```json
{
  "document_type": "invoice",
  "vendor_name": "Aurora Office Supplies Demo LLC",
  "invoice_number": "AUR-2026-051",
  "issue_date": "2026-05-31",
  "total_amount": 1248.5,
  "tax_amount": 80.0,
  "currency": "USD",
  "line_items": [
    {
      "description": "Printer paper",
      "quantity": 5,
      "unit_price": 18.5,
      "amount": 92.5
    }
  ],
  "confidence": 0.82
}
```

Adapter output rules：

- `ParserResult.parser_source` 與欄位層級 `ExtractedField.parser_source` 必須是 `vlm_invoice`，fallback 後才會是 `deterministic_invoice`。
- `DocumentFields` 欄位仍使用 `document_type`、`vendor_name`、`invoice_number`、`issue_date`、`total_amount`、`tax_amount`、`currency` 與 `line_items`。
- `confidence` 需落在 `0` 到 `1`；未知或 invalid confidence 不可硬填高分。
- `source_text` 在 v0.27.1 起優先來自 matched OCR line；沒有 OCR context 或無法對齊時可為 `null`，並以 `fallback_reason=evidence_unavailable` / `evidence_unmatched` 說明，不得假造 page 或 bbox。
- `trace_metadata` 必須標示 `parser_route=vlm_first`、`vlm_provider`、`vlm_model`、`source_input_type=image`、`fallback_chain` 與 `fallback_reason`。

### Fallback Policy

Fallback 不得覆蓋既有 OCR / indexing 狀態，也不讓 Agent 直接呼叫 VLM：

| Failure | Parser behavior |
|---|---|
| Provider disabled / unavailable | 記錄 `fallback_reason=vlm_provider_unavailable`，執行 `deterministic_invoice` fallback。 |
| Request timeout | 記錄 `fallback_reason=vlm_timeout`，執行 deterministic fallback。 |
| Unsupported or unsafe file | 記錄 resolver failure reason，例如 `unsupported_file` 或 `unsafe_path`，執行 deterministic fallback。 |
| Invalid JSON / missing required fields | 記錄 `fallback_reason=vlm_invalid_response` 或 `vlm_missing_fields`，不產生假欄位，執行 deterministic fallback。 |
| Confidence too low | 記錄 `fallback_reason=vlm_low_confidence`，執行 deterministic fallback。 |

Phase 25 Agent contract 不變：`get_document_fields` 只讀已保存的 `ParserResult` / `DocumentFields`。Agent 不直接呼叫 VLM、不改 tool allowlist，也不新增任意 SQL、shell、file system command、worker、DB 或 permission model。

### 26-03 Runtime Notes

- `get_document_parser()` now builds a VLM-first `VlmInvoiceParser` unless `DOCURAG_PARSER_SOURCE=deterministic_invoice` is explicitly set.
- The default `ollama` provider uses the local HTTP `/api/generate` shape with `stream=false`, `format=json`, image base64 and compact OCR context; `DOCURAG_VLM_PROVIDER=fake` is a built-in demo / smoke stub and is not a production VLM runtime.
- Ollama response parsing accepts JSON in `response`, JSON in `thinking` when `response` is empty, markdown fenced JSON and the first JSON object embedded in text. Amount-like strings, confidence labels and line item `total` / `total_price` / `subtotal` aliases are normalized before writing the existing `DocumentFields` schema.
- VLM success returns `ParserResult.parser_source=vlm_invoice` and field-level `parser_source=vlm_invoice`.
- Provider unavailable, timeout, invalid response, missing required fields, unsupported file or low confidence falls back to `deterministic_invoice`; fallback details are preserved in `trace_metadata.fallback_chain` and `trace_metadata.fallback_reason`.
- Existing Phase 25 Agent APIs are unchanged because `get_document_fields` reads the saved `ParserResult` regardless of parser source.

### 26-04 Source Comparison Notes

- Parser responses expose the active route through `trace_metadata.parser_route`: `vlm_first` for Phase 26 default path and `deterministic_only` for explicit deterministic override.
- `trace_metadata.fallback_chain` shows either `vlm_invoice`, `vlm_invoice -> deterministic_invoice` or `deterministic_invoice`.
- VLM fallback promotes the VLM / resolver reason to top-level `ParserResult.fallback_reason`; if deterministic fallback also has missing fields, its reason is preserved as `trace_metadata.deterministic_fallback_reason`.
- `trace_metadata.confidence_summary` provides a compact confidence value that smoke scripts or API clients can check without a production parser comparison dashboard.

### 26-05 Demo Release Notes

- Release version is `v0.26.0`.
- `scripts/demo-smoke-test.ps1` validates the VLM-first fallback path on text input and, when `DOCURAG_VLM_PROVIDER=fake` is set for the backend / script environment, validates the `vlm_invoice` success path on image input.
- The same smoke path verifies that Agent `get_document_fields` can read both `deterministic_invoice` fallback results and `vlm_invoice` success results without changing the Phase 25 Agent tool contract.

## Phase 27 OCR / VLM Evidence Alignment

v0.27.1 補強 VLM parser 的 evidence contract。OCR 仍負責產生可搜尋文字層、OCR lines、chunks 與 RAG citations；VLM parser 負責欄位理解，但 request 會同時帶原始圖片與 compact OCR context。

VLM request boundary：

- 必須包含 demo-safe uploaded image。
- 若 OCR 已完成，descriptor 會附帶最多 30 筆 compact OCR context lines，包含 text、page number、bbox 與 confidence 摘要。
- VLM provider 不可用、unsupported file、timeout、invalid response、missing fields 或 low confidence 時，仍 fallback 到 deterministic parser。

VLM field evidence rules：

- `vlm_invoice` success path 沿用既有 `DocumentFields` / `ExtractedField` / `ParserResult` schema，不新增平行 parser schema。
- 欄位值若可對回 OCR line，欄位結果會保存 `source_text`、`source_page` 與 `source_bbox`；confidence 取 VLM confidence 與 OCR line confidence 的較保守值。
- 欄位值若無法對回 OCR line，欄位 `fallback_reason` 會標示 `evidence_unmatched`；沒有 OCR context 時標示 `evidence_unavailable`。
- `ParserResult.trace_metadata` 會包含 `ocr_context_state`、`ocr_context_line_count`、`field_evidence_state`、`field_evidence_matched_count` 與 `field_evidence_unmatched_count`。
- RAG / vector indexing 仍只使用 OCR chunks；VLM structured fields 不會在此 ticket 自動寫入 retrieval corpus。
- Agent planner / tool allowlist 不變；Agent 透過 `get_document_fields` 讀 structured fields，透過 `search_documents` 讀 OCR chunks。

## Phase 27 Aggressive Demo Defaults

Phase 27 將已完成且有 fallback 的進階能力改成預設體驗。這是 demo default，不代表 production DB、worker、auth、OpenAI API 或 vLLM serving 已完成。

### Default Runtime Env

| Env | Default | Meaning |
|---|---|---|
| `DOCURAG_RAG_RETRIEVAL_PROVIDER` | `hybrid_rerank` | `/rag/query` 與 Agent `search_documents` 預設先做 keyword + vector merge，再嘗試 rerank。 |
| `DOCURAG_EMBEDDING_PROVIDER` | `ollama` | Query / indexing embedding 預設使用 Ollama `POST /api/embed`。 |
| `DOCURAG_RERANK_PROVIDER` | `fastembed` | Reranker adapter 預設使用 FastEmbed lazy import；runtime 不可用時保留 candidates 並寫入 fallback metadata。 |
| `DOCURAG_QDRANT_URL` | `http://127.0.0.1:6333` | Local Qdrant endpoint；Docker Compose 內預設改用 `http://qdrant:6333`。 |

### RAG Provider Behavior

- `keyword`：只使用 local keyword retrieval，可作 debug / validation override。
- `vector`：使用 Ollama embedding + Qdrant search，失敗時 fallback 到 keyword evidence。
- `vector_rerank`：先使用 vector retrieval，再用 reranker 重新排序；vector failure 時不再 rerank fallback chunks。
- `hybrid`：合併 keyword + vector candidates，vector branch failure 時回到 keyword-only candidates 並保留 branch fallback metadata。
- `hybrid_rerank`：Phase 27 default；先 hybrid merge / dedupe，再交給 reranker。embedding、Qdrant 或 reranker 不可用時都不得讓 request hard fail。

### Frontend Ingestion Behavior

Admin / Analyst ingestion surface v0.27.0 起預設為第一屏。Phase 30 focused hardening 起，檔案選擇器可一次選多個檔案；frontend 會在單一頁面 session 內逐檔走既有 upload / source router / provider-selected OCR / parser / vector indexing 流程，並分檔顯示成功或失敗。這只是 frontend orchestration，不新增 batch upload API、async queue、worker 或 DB-backed ingestion pipeline。

上傳與 provider-selected OCR 成功後，frontend 會 best-effort 呼叫：

1. `POST /documents/{document_id}/parse`
2. `POST /documents/{document_id}/index/vector`

任一呼叫失敗時只顯示 fallback / unavailable message，不阻斷文件保存、local chunks 或 Viewer Chat fallback 查詢。
