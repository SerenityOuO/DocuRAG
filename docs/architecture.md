# MVP Architecture

本文件描述 DocuRAG AgentOps 目前的受控 MVP 架構。到 v0.33.0 為止，專案已完成 backend / frontend demo、provider-selected OCR、citation trace、retrieval eval runner、built-in RAG eval admin API、vector / rerank / hybrid / `hybrid_rerank` retrieval building blocks、Viewer Chat / Admin Ingestion role split、deterministic Agent tool-use trace、VLM-first parser provider spike、OCR / VLM evidence alignment、aggressive demo defaults、`.txt` direct ingestion、text-native PDF extraction、demo auth mode、後台「測試RAG」surface、opt-in PostgreSQL metadata repository foundation、formal Auth / RBAC / tenant boundary release，以及 Redis + NATS worker demo milestone。Phase 33 `33-01` 固定 Redis / NATS worker pipeline contract；`33-02` 新增 opt-in Redis runtime slice，用於 session cache、RAG query cache 與 rate limit，Redis 未設定或不可用時仍走 fallback；`33-03` 新增 demo-safe NATS helper、worker skeleton 與 task status API；`33-04` 完成 worker demo smoke 與 release sync。Phase 34 `34-02` / `34-03` 已補上 demo-safe scanned PDF page image rendering 與 page-level OCR status / retry path。這不代表已完成 production NATS event bus、durable async worker、production eval dashboard、production scanned PDF OCR accuracy tuning 或 layout understanding。

## MVP Shape

```text
Viewer Chat Surface
    |
    |-- RAG answer / answer source / retrieval source / citations
    |
Demo Auth Gate
    |
    |-- optional Admin / Analyst / Viewer login mode
    |
Admin / Analyst Ingestion Surface
    |
    |-- upload / provider-selected OCR / processing status
    |-- OCR result / local chunks / metadata debug links
    |-- Phase 24 parser result: OCR text -> structured fields
    |-- Phase 26 / 27 parser route: image input + OCR context -> vlm_invoice -> deterministic fallback
    |-- Phase 29 built-in RAG eval: fixed hybrid_rerank Chinese invoice benchmark
    |-- Phase 25 / 38 Agent contract: deterministic fallback -> permission-guarded tools -> trace
    |
FastAPI Backend
    |
    |-- demo auth API / role guard dependencies
    |-- formal signed bearer guard / project access filtering
    |-- health / document API / OCR API / RAG API / parse / fields API
    |-- Agent run / lookup API
    |-- manual vector indexing API
    |-- built-in RAG eval API / retrieval eval runner CLI
    |
Phase 33 Redis Slice / Worker Pipeline Skeleton
    |
    |-- opt-in Redis session cache / query cache / rate limit
    |-- NATS publish / subscribe helper
    |-- worker skeleton placeholder handlers
    |-- NATS / JetStream event topics
    |-- task status / retry / idempotency policy
    |
Local Data Store
    |
    |-- uploads / metadata JSON / OCR results / chunks / parser results / future Agent runs
    |
Optional Local AI Runtime
    |
    |-- PaddleOCR GPU provider
    |-- Phase 26 VLM parser provider over local HTTP
    |-- Ollama generation / embedding
    |-- Qdrant vector collection
    |-- FastEmbed rerank adapter
```

MVP 的預設路徑在 v0.27.0 改為 aggressive demo defaults：`/rag/query` 與 Agent `search_documents` 預設使用 `hybrid_rerank`，先合併 keyword 與 vector candidates，再嘗試 rerank。沒有 Ollama embedding、Qdrant 或 FastEmbed runtime 時，request 仍回到 keyword evidence，並在 trace metadata 標明 vector / rerank fallback。

Phase 23 的 role split 是 demo surface 與產品敘事邊界，不是正式權限系統。Viewer Chat 不提供上傳或 OCR 操作；Admin / Analyst ingestion surface 可以呼叫既有 backend upload / OCR API，並在 Phase 24 後顯示 deterministic parser structured fields。Phase 25 Agent surface 仍屬於 Admin / Analyst / developer-oriented demo，不進入 Viewer Chat 主流程。

Phase 28 的 demo auth mode 只把這個 role split 變成可登入展示的本機切片：`DOCURAG_AUTH_MODE=demo` 時，frontend 會顯示 Admin / Analyst / Viewer login，backend 會對 upload、OCR、mock OCR、parse 與 vector index 做 role guard。Download 在 demo mode 下需要登入，但三種角色都可使用。這不是 tenant isolation、project permission、正式 session store 或 production RBAC。

Phase 29 的「測試RAG」只把既有 retrieval eval runner 包成後台可操作的 built-in benchmark。它固定 `hybrid_rerank` 與 synthetic 中文發票 dataset，只顯示第一版核心 metrics；fallback cases 以摺疊明細呈現。這不是 strategy comparison UI、production eval dashboard、eval history storage、自訂 dataset builder、OCR eval、VLM parser eval 或 LLM-as-judge。

## Phase 33 Redis / NATS Worker Pipeline Boundary

`33-01` 固定 worker pipeline 的文件合約。`33-02` 只啟用最小 Redis backend slice：當 `DOCURAG_REDIS_URL` 為空時，系統維持既有 fallback-only demo；當 Redis 設定存在時，backend 會 best-effort 使用 Redis 做 demo-safe session cache、RAG query cache 與 rate limit。Redis 不可用時 `/health` 會顯示 `redis=unavailable`，RAG request 仍可繼續，並在 trace metadata 標示 cache / rate-limit fallback 狀態。`33-03` 新增 NATS publish / subscribe helper、worker skeleton placeholder handlers、`worker_tasks.json` task status store 與 `/tasks` read API，讓 publish / consume / status update 可以被 smoke 驗證。

`33-03` 不把 OCR、parser、indexing 或 eval 的核心 model 行為搬進 production async queue，也不新增 K8s autoscaling、dead-letter dashboard、full observability stack、vLLM、OpenAI API、fine-tuning 或 Agent planner 變更。同步 API 與現有 frontend best-effort orchestration 仍維持現況。

Redis responsibilities：

| Responsibility | Intended use | Boundary |
|---|---|---|
| Session cache | Future formal auth session / refresh metadata cache。 | 不保存 password、raw secret 或 production identity provider state；不得取代 backend Auth / RBAC guard。 |
| Query cache | 短 TTL 快取 project-scoped RAG query result 或 retrieval candidates。 | Cache key 必須包含 organization / project / role / provider config；不得跨 tenant 共用。 |
| Rate limit | 依 user、organization、IP 或 API group 記錄短期 counter。 | 只做節流輔助，不是 audit log 或 permission source of truth。 |
| Worker lock | 以 idempotency key 防止同一 document / task 重複處理。 | Lock 必須有 TTL；不得作長期 task status 或資料庫替代品。 |
| Short-term chat history | 保存短期 conversation context 或 UI draft。 | 不保存 canonical citations、document chunks、Agent run history 或 eval result。 |

`33-02` runtime coverage：

- Demo login 成功後可 best-effort 寫入 token hash session cache；token 本身仍由 existing signed bearer guard 驗證，Redis 不是權限來源。
- `/rag/query` 會用 project / role / provider / visible document signature 建立 query cache key；cache hit 直接回傳已序列化的 `RagQueryResponse`。
- `/rag/query` 會用 Redis counter 做每分鐘簡單 rate limit；Redis unavailable 時不封鎖 request，只回到原本 demo 路徑。
- Redis Python client 收斂在 optional `backend[redis]` extra；Docker image 需以 `DOCURAG_INSTALL_REDIS=true` 建置才會安裝 client。
- Docker Compose 提供 `redis` profile，可用 `DOCURAG_INSTALL_REDIS=true DOCURAG_REDIS_URL=redis://redis:6379/0 docker compose --profile redis ...` 明確啟用。

NATS / JetStream topics：

| Topic | Producer | Consumer | Payload boundary |
|---|---|---|---|
| `document.uploaded` | Document upload API | Future router / OCR dispatcher | `document_id`、`organization_id`、`project_id`、`source_type`、`actor_user_id`。不得附 file bytes。 |
| `document.ocr.requested` | API / worker dispatcher | OCR worker | `document_id`、`task_id`、provider hints、idempotency key。 |
| `document.parse.requested` | API / OCR completion worker | Parser worker | `document_id`、`task_id`、parser source policy、idempotency key。 |
| `document.index.requested` | API / parser completion worker | Indexing worker | `document_id`、`task_id`、chunk source version、idempotency key。 |
| `rag.eval.requested` | Admin / Analyst eval API | Eval worker | `eval_run_id`、dataset id、strategy、project id、idempotency key。 |

`33-03` runtime coverage：

- `DOCURAG_NATS_URL` 預設為空，NATS helper 回 `disabled`；`memory://` 可用於本機 smoke，不需要真實 NATS server。
- 真實 NATS client 收斂在 optional `backend[nats]` extra；Docker image 需以 `DOCURAG_INSTALL_NATS=true` 建置才會安裝 client。
- Docker Compose 提供 `nats` profile，可用 `DOCURAG_INSTALL_NATS=true DOCURAG_NATS_URL=nats://nats:4222 docker compose --profile nats ...` 明確啟用。
- `WorkerSkeleton` 會訂閱 OCR、parser、indexing、eval topics，placeholder handler 只把 task status 從 `queued` 更新到 `running` 再到 `succeeded`。
- `GET /tasks` 與 `GET /tasks/{task_id}` 讀取 `worker_tasks.json` 中的 task records；formal auth mode 會依 project access 過濾或拒絕 cross-project task。

Event payload contract：

```json
{
  "event_id": "evt_01HX...",
  "schema_version": "phase33.worker_event.v1",
  "event_type": "document.ocr.requested",
  "occurred_at": "2026-06-07T14:30:00Z",
  "organization_id": "org_demo",
  "project_id": "project_demo",
  "actor_user_id": "user_admin",
  "document_id": "doc_123",
  "task_id": "task_123",
  "idempotency_key": "ocr:project_demo:doc_123:source_v1",
  "attempt": 1,
  "trace_id": "trace_123"
}
```

Task status lifecycle：

| Status | Meaning |
|---|---|
| `queued` | Task 已建立並等待 worker 消費。 |
| `running` | Worker 已取得 lock 並開始執行。 |
| `retrying` | 暫時性失敗，等待 backoff 後重試。 |
| `succeeded` | Task 完成且結果已寫回 canonical store。 |
| `failed` | Task 結束且不再重試，需保存 failure reason。 |
| `cancelled` | Task 被明確取消或被新版同類 task 取代。 |

Task status schema 至少包含 `task_id`、`task_type`、`status`、`organization_id`、`project_id`、`document_id` 或 `eval_run_id`、`idempotency_key`、`attempt`、`max_attempts`、`created_at`、`started_at`、`updated_at`、`finished_at`、`failure_reason`、`error_code` 與 `trace_metadata`。`33-03` 先保存到 local JSON `worker_tasks.json`；future DB-backed worker task table 或 PostgreSQL migration 仍留給後續 ticket。

Retry / failure policy：

- Transient failures such as `provider_unavailable`, `qdrant_unavailable`, `rate_limited` or `worker_lock_conflict` may retry with exponential backoff and jitter.
- Terminal failures such as `permission_denied`, `project_access_denied`, `unsupported_file`, `invalid_input`, `unsafe_path` or `schema_validation_failed` must not retry automatically.
- Default max attempts for worker tasks is 3 unless a later implementation ticket defines a stricter value.
- Every retry must preserve the same `idempotency_key`, increment `attempt` and keep the original `trace_id`.

Idempotency key policy：

- Key format should be deterministic: `{task_type}:{project_id}:{resource_id}:{source_version}:{request_fingerprint}`.
- Replaying the same event with the same key must not duplicate OCR results, parser fields, vector points, eval runs or Agent traces.
- New source version, changed parser policy or changed indexing strategy should create a new key rather than mutate a completed task silently.

## Phase 24 Parser Contract Boundary

`24-01` 只固定 VLM-compatible parser contract，不實作 runtime。Phase 24 的目標是讓後續 tickets 可以用 deterministic invoice parser fallback 展示 OCR 後的 structured fields，同時保留 future LLM / VLM parser 替換位置。

```text
Admin / Analyst Ingestion Surface
    |
    |-- upload document
    |-- run provider-selected OCR
    |-- run parser explicitly
    |
FastAPI Backend
    |
    |-- OCR text / OCR lines
    |-- ParserResult(status, fields, fallback metadata)
    |
Local JSON Store
    |
    |-- document metadata
    |-- OCR result / chunks
    |-- future fields result
```

Parser contract model：

- `DocumentFields` 固定 invoice MVP 欄位：`document_type`、`vendor_name`、`invoice_number`、`issue_date`、`total_amount`、`tax_amount`、`currency` 與 `line_items`。
- `ExtractedField` 保留欄位值、`confidence`、`source_text`、`source_page`、`source_bbox`、`parser_source` 與 `fallback_reason`。
- `ParserResult` 保留 document id、parser status、schema version、fields、source OCR status、updated time 與 trace metadata。
- Parser status 使用 `pending`、`parsing`、`parsed`、`failed`；後續若接 document processing metadata，才新增可選 `processing.parser=pending/running/completed/failed`。
- Parser failure 不覆蓋 OCR / indexing 狀態，也不影響 Viewer Chat 的 default RAG path。

Parser source boundary：

| Parser source | Input | Runtime boundary |
|---|---|---|
| `deterministic_invoice` | OCR text / OCR lines | Phase 24 MVP fallback，規則式抽取，不新增外部依賴。 |
| `llm_invoice` | OCR text / OCR lines | Future text-only parser，不屬於 `24-01`。 |
| `vlm_invoice` | 原始圖片、layout trace 或 OCR trace | Future VLM parser，不屬於 `24-01`，不在 MVP 中宣稱 production-ready。 |

Viewer Chat surface 仍只查詢已建立知識庫，不顯示 upload、OCR 或 parse 操作。Parser result 先服務 Admin / Analyst ingestion flow 的 structured fields 摘要，不提前接 SQL query tool、Agent tool、default vector metadata filtering 或 production parser dashboard。

## Phase 25 Agent Tool-use Contract Boundary

`25-01` 只固定 Agent MVP contract，不實作 runtime。Phase 25 的目標是用 deterministic planner 與 allowlisted read-only tools，把 Phase 24 structured fields、既有 document search / retrieval 與 deterministic invoice summary 串成可驗證 trace。

```text
Admin / Analyst / Developer Demo Surface
    |
    |-- run demo-safe Agent task
    |-- view plan / tool calls / observations / final answer
    |
FastAPI Backend
    |
    |-- future POST /agent/run
    |-- future GET /agent/runs/{run_id}
    |-- deterministic planner
    |
Allowlisted Read-only Tools
    |
    |-- get_document_fields -> local parser result
    |-- search_documents -> existing document search / keyword retrieval
    |-- summarize_invoice_fields -> deterministic formatter
    |
Local JSON Store
    |
    |-- document metadata
    |-- OCR result / chunks
    |-- parser result
    |-- future Agent run result
```

Agent contract model：

- `AgentRun` 固定 `run_id`、`status`、`task`、可選 `document_id` / `query`、`plan_steps`、`tool_calls`、`final_answer`、`citations`、`trace`、`created_at` 與 `updated_at`。
- `AgentStep` 描述 deterministic plan：步驟順序、預期 tool、狀態、input summary、observation summary 與 fallback reason。
- `AgentToolCall` 描述 allowlisted tool execution：tool name、status、input、output summary、observation、citations、trace metadata 與 error message。
- `final_answer` 必須由 tool observation 與可用 citations 組成；缺資料時記錄 fallback，不硬填欄位。
- Agent trace 必須標明 planner 為 `deterministic`，tool policy 為 `allowlisted_read_only`。

Allowlisted tools：

| Tool | Runtime boundary |
|---|---|
| `get_document_fields` | 只讀既有 local JSON metadata 中的 `ParserResult` / `DocumentFields`。 |
| `search_documents` | 只使用既有 document search / keyword retrieval path，不修改 ranking、不觸發 indexing。 |
| `summarize_invoice_fields` | 只用 deterministic formatter 摘要 invoice fields，不呼叫 LLM。 |

Planner boundary：

- Invoice summary task 且有 `document_id` 時，固定執行 `get_document_fields` -> `search_documents` -> `summarize_invoice_fields`。
- Document question task 可只執行 `search_documents` 並產生 source-backed fallback answer。
- Missing parser fields、search miss 或 unsupported task 必須回傳 failed / fallback step，不嘗試任意工具。

Agent guardrails：

- 不接 LLM autonomous planner、OpenAI function calling、Ollama planning call、streaming agent 或新外部依賴。
- 不允許任意 SQL、任意 tool execution、delete、reindex、file system command、shell command、任意 HTTP side effect 或 destructive operation。
- 不新增 PostgreSQL、Redis、NATS、worker、async queue、Auth、RBAC、role guard、project permission 或 multi-user isolation。
- 不修改 parser extraction、OCR provider、RAG ranking、eval runner、Qdrant indexing 或 default Viewer Chat path。
- Agent trace surface 不宣稱 production Agent dashboard 或正式權限系統。

## Phase 38 Agent Runtime Permission Contract

`38-01` 固定 Agent runtime hardening 的 planner、tool permission、fallback 與 trace contract。這是文件合約，不新增 LLM planner runtime、不新增 tool execution code，也不改 Auth / RBAC schema、RAG ranking、OCR 或 parser behavior。

Planner boundary：

- `deterministic` planner 是 always-available fallback，也是目前可執行的安全基準。LLM planner 未啟用、timeout、回傳 invalid plan、選到未允許工具、缺少必要 evidence 或 plan schema validation 失敗時，都必須回到 deterministic fallback 或回傳明確 failed state。
- Future `llm_planner` 只能作為明確啟用的 provider boundary。它的輸出必須是結構化 plan，只能從 request role / project context 與 allowed tools 中選擇步驟，不得自行發明工具、參數或跨 project 讀寫。
- Planner timeout、invalid JSON / invalid schema、unsafe tool selection、missing required input、citation / observation 不足時，都必須記錄 `planner_fallback_reason`，並且不得執行任何未通過 permission guard 的 tool。

Tool tiers：

| Tier | Allowed boundary | Permission requirement |
|---|---|---|
| `read-only` | 只讀目前使用者可存取 project 內的文件、parser fields、retrieval evidence、eval result 或既有 Agent run。 | 需要有效 role 與 project access；不需要 human confirmation。 |
| `write` | 只能建立或更新 project-scoped、可回溯、非 destructive 的應用資料。Phase 38 後續 runtime ticket 若要開放，必須逐項 allowlist。 | 需要 Analyst / Admin、project access 與 explicit permission guard；需要 human confirmation。 |
| `admin` | 只限 project / organization 管理型動作，必須可 audit。Phase 38 `38-01` 不新增此類 runtime。 | 需要 Admin、project access、audit trace 與 human confirmation。 |
| `destructive` | 刪除、drop、reindex destructive mode、不可逆資料改動、外部 side effect、任意 SQL、shell、filesystem command、network tool 或 secret / credential 變更。 | Phase 38 contract 視為 prohibited；後續若要新增，必須另有 ticket、明確 rollback / approval policy 與更嚴格 validation。 |

Permission guard rules：

- Tool selection 前與 tool execution 前都必須檢查 role、project access、tool allowlist、tool tier、input schema 與 target resource project。
- Viewer 只能走 read-only 查詢與 trace lookup；Analyst / Admin 才可能在後續 ticket 被允許 write / admin tool。任何跨 project、unknown tool、unknown tier、schema 外參數或不符合 role 的 tool request 都必須被拒絕。
- Human confirmation requirement 是 trace contract 的一部分：read-only 可為 `not_required`；future write / admin 必須是 `required` 且在 confirmed 前不得 execution；destructive 在 Phase 38 `38-01` 中一律 unavailable。
- Permission guard 不得被 LLM planner、provider fallback、manual override 或 smoke script 繞過。

Trace contract：

- Plan trace 必須包含 `planner_provider`、`planner_status`、`planner_latency_ms`、`planner_fallback_reason`、`plan_id`、`plan_steps` 與 `plan_validation_status`。
- Tool selection trace 必須包含 `tool_name`、`tool_tier`、`permission_decision`、`required_role`、`project_id`、`project_access`、`human_confirmation_required` 與 `human_confirmation_status`。
- Observation / reflection trace 必須包含 `observation_summary`、`citations`、`reflection`、`fallback_reason`、`final_answer_source` 與 final answer status。
- Trace 不得記錄 production secret、raw bearer token、API key、private credential 或未遮罩的敏感設定。

Forbidden boundary：

- Phase 38 contract 明確禁止任意 SQL、shell command、filesystem command、arbitrary network tool、delete、drop table、destructive reindex、credential mutation、production database mutation 或任何 destructive tool。
- `38-01` 不修改既有 Agent run API 行為；後續 `38-02` / `38-03` 若實作 runtime，必須先符合本 contract。

## Phase 43 AgentOps Governance Contract

`43-01` 是 Agent governance contract ticket，只定義 governance / secure tool runtime 邊界，不新增 runtime tool execution、不新增 tool、不修改 deterministic Agent planner，也不改 OCR、parser、RAG 或 inference 行為。它承接 Phase 38 的 permission guard：Phase 38 已讓既有 read-only Agent tools 可被 role / project / tier guard 控制；Phase 43 則把後續面試可展示的治理資料邊界固定下來，讓 tool policy、risk score、approval、audit 與 replay 有一致語意。

Relationship to deterministic Agent MVP：

- Phase 25 / Phase 38 的 deterministic planner 與既有 allowlisted read-only tools 仍是目前唯一可執行路徑。
- Phase 43 不把 Agent 升級成 production autonomous Agent，不開放 arbitrary SQL、shell、filesystem command、external side-effect tool 或 destructive tool runtime。
- 後續 runtime ticket 若要新增 write / admin tool，必須逐項 allowlist，並在執行前通過 role、project access、tool tier、risk score、approval state 與 input schema guard。

Agent governance tool tiers：

| Tier | Governance boundary | Approval / risk contract |
|---|---|---|
| `read-only` | 只讀使用者可存取 project 內既有資料，例如文件、parser fields、retrieval evidence、eval result 或 Agent run。 | `risk_score` 通常為 low；`approval_state=not_required`；仍需 permission / project access check。 |
| `write` | 建立或更新 project-scoped、可回溯、非 destructive 的應用資料；必須由後續 runtime ticket 明確 allowlist。 | 需要 Analyst / Admin、project access、`approval_state=required` 或明確 approved state；需 audit event。 |
| `admin` | project / organization 管理型動作；必須可 audit，且不得由 planner 自行發明。 | 需要 Admin、project access、較高 `risk_score`、approval 與 audit event。 |
| `destructive` | 刪除、drop、destructive reindex、不可逆資料改動、任意 SQL、shell、filesystem command、network side effect、secret / credential mutation。 | 在 Phase 43 contract 中仍為 prohibited boundary；若未來 ticket 要新增，必須另有 rollback / approval / data safety 規範。 |

Tool policy boundary：

- `tool_name`、`tool_tier`、`allowed_roles`、`project_access_required`、`risk_score`、`approval_required`、`side_effect_policy`、`audit_required` 與 `replay_supported` 必須可由文件或 trace 解釋。
- `risk_score` 是治理判斷資料，不是模型信心分數；它描述 tool call 的資料改動、跨 project 風險、外部 side effect 與回復難度。
- Unknown tool、unknown tier、schema-extra input、cross-project request、unapproved write / admin request 或任何 destructive request 都必須 fail closed，且不得洩漏 unauthorized resource details。

Approval state boundary：

| State | Meaning |
|---|---|
| `not_required` | read-only 或低風險 tool call，permission check 通過即可執行。 |
| `required` | tool call 需要 human approval；未 approved 前不得執行。 |
| `approved` | 已由允許角色確認，可在同一 policy snapshot 下執行。 |
| `rejected` | human reviewer 拒絕；Agent run 必須停止該 tool call 並保留 generic reason。 |
| `expired` | approval 已過期或 policy snapshot 已不一致；不得沿用舊核准。 |

Audit / replay event boundary：

- Audit event 至少需能描述 `event_id`、`run_id`、`step_id`、`tool_name`、`tool_tier`、`risk_score`、`actor_role`、`project_id`、`permission_decision`、`approval_state`、`reason_code` 與 timestamp；不得保存 raw bearer token、API key、secret 或 private credential。
- Replay event 至少需能描述 `replay_id`、`source_run_id`、`policy_snapshot_id`、`tool_policy_snapshot`、`input_summary`、`observation_summary`、`citations`、`fallback_reason`、`final_answer_source` 與 replay result status。
- Replay 預設是 inspection / eval artifact，不重新執行 destructive 或 external side-effect tools；若後續 ticket 實作 replay runtime，必須保留 original run 與 replay run 的 policy snapshot 差異。

Trace completeness boundary：

- Agent run trace 必須保留 planning、tool selection、permission / approval decision、observation、reflection / fallback、citation evidence 與 final answer source。
- Trace 欄位不足時，Agent eval 只能標示 evidence incomplete 或 replay not available，不得假裝 governance evidence 完整。

43-02 Tool permission policy runtime：

- 既有 allowlisted Agent tools 仍只有 `get_document_fields`、`search_documents` 與 `summarize_invoice_fields`，全部維持 `read-only` tier、`no_side_effects` policy 與 Admin / Analyst required roles。
- Runtime policy metadata 現在會輸出 `risk_tier=low`、`risk_score=10`、`approval_required=false` 與 `approval_state=not_required`；這是治理 trace metadata，不新增 approval workflow。
- Agent run-level trace 會彙總 `risk_tiers`、`risk_scores`、`approval_required` 與 `approval_state`，讓 Viewer blocked path 即使沒有 tool call 也能留下 generic permission trace。
- Viewer role 會在 tool execution 前被擋下，final answer / trace 只保留 generic `tool_permission_forbidden` 與 denied tool name；不暴露 cross-project target document 或 unauthorized resource details。
- 本 runtime slice 不新增 write / admin / destructive tool，不新增任意 SQL、shell、filesystem command、external side-effect tool、production IAM、SSO、OAuth、MFA 或外部 approval service。

43-03 Human approval / risk tier boundary：

- Permission evaluator 會對 `approval_required=true` 且 `approval_state` 不是 `approved` 的 high-risk policy fail closed。`required` 對應 `approval_required`、`rejected` 對應 `approval_rejected`、`expired` 對應 `approval_expired`。
- `approved` 只代表同一 policy snapshot 下可通過 approval gate，仍必須先通過 role、project access、tool tier 與 side-effect policy guard。
- Runtime 目前沒有 write / admin / destructive allowlisted tool；測試以 monkeypatched policy 驗證 skip-safe path，確保 future high-risk tool 不會靜默執行。
- API / trace 呈現等待 approval 或 rejected state 時，應使用 `permission_decision=forbidden`、`permission_reason=approval_required|approval_rejected|approval_expired`、`approval_required=true`、`approval_state=<state>` 與既有 `risk_tier` / `risk_score`。
- Frontend 若後續 ticket 呈現 approval state，應只讀 trace metadata，不自行判斷或覆寫 permission decision；本 ticket 不新增 UI。

43-04 Agent replay / eval artifact boundary：

- `sample-data/eval/agent-replay-sample.json` 是 inspection-only replay artifact，保存 source run id、policy snapshot、plan steps、tool calls、observations、citations、fallback reason 與 final answer source。
- `scripts/agent-replay-smoke.ps1` 只讀 replay artifact 並產生 deterministic report；它不呼叫 backend API、不重新執行 Agent tools、不連線外部服務，也不執行 SQL、shell、filesystem 或 destructive tool。
- Replay eval dimensions 固定為 tool correctness、permission compliance、evidence coverage、fallback reason 與 groundedness notes；groundedness 是 citation / observation coverage note，不是 LLM-as-judge。
- `sample-data/eval/agent-replay-report.json` 是 demo-safe evidence report，可用來檢查 tool selection、permission guard、observation coverage、fallback reason 與 final answer 是否保留可追溯證據。

## Phase 44 Document Intelligence QA Contract

`44-01` 是 Document Intelligence QA / human review loop 的 contract ticket，只定義 OCR / VLM parser 結果如何被檢查、修正與量化，不新增 runtime、不修改 parser / OCR default behavior，也不新增 full annotation platform、production workflow、多人審核權限或外部 labeling tool。

Relationship to existing OCR / VLM evidence alignment：

- Phase 24 / 26 / 27.1 已讓 `ExtractedField` 保留 `confidence`、`source_text`、`source_page`、`source_bbox`、`parser_source` 與 `fallback_reason`；Phase 44 在這些欄位上定義 QA / review 語意，不新增平行 parser schema。
- Phase 34 scanned PDF OCR blocks 已保留 page、bbox 與 confidence；Phase 44 可以引用這些 evidence，但不得假造 layout analysis、table reconstruction、deskew result 或 production OCR accuracy score。
- Agent `get_document_fields` 仍只讀已保存 parser result；Phase 44 不讓 Agent 直接修改欄位、不新增任意 tool、不改 RAG ranking 或 VLM parser prompt。

Field QA metadata boundary：

| Field | Meaning |
|---|---|
| `field_confidence` | 欄位可信度，沿用 parser / VLM / OCR evidence 的 `0..1` 分數；未知時為 `null`，不可硬填高分。 |
| `evidence_source` | 欄位證據來源，例如 `ocr_line`、`vlm_ocr_match`、`vlm_unmatched`、`manual_correction` 或 `unavailable`。 |
| `source_page` / `source_bbox` | 來自 OCR line、page OCR block 或既有 VLM evidence alignment；沒有來源時保持 `null`。 |
| `review_status` | human review 狀態，最小集合為 `unreviewed`、`needs_review`、`confirmed`、`corrected`、`rejected`。 |
| `correction_version` | 人工修正版本，從原始 parser result 的 `0` 開始；每次人工修正遞增，保留 original value 供 eval 比較。 |

Parser field accuracy metrics：

- `field_accuracy` 用 golden labels 對比 parser output，可用 exact / normalized match 計算；此指標不是 LLM-as-judge。
- `missing_field_count` 統計 golden label 有值但 parser 未產生可用值的欄位。
- `wrong_value_count` 統計 parser 值存在但與 golden label 不一致的欄位。
- `evidence_mismatch_count` 統計欄位值雖可能正確，但 `source_text`、`source_page` 或 `source_bbox` 無法對回 golden evidence 的情況。
- 指標需可回溯到 document id、field name、parser source、correction version 與 golden label version；不得把 eval 結果寫成 production OCR guarantee。

Human correction / golden labels boundary：

- Human correction 是 demo-safe review artifact：保存欄位名稱、原始 parser value、corrected value、review status、correction version、review note 與 evidence reference。
- Golden labels 是 parser / VLM eval 的輸入資料，不是 model training dataset、production annotation task queue 或多人審批流程。
- Golden labels 至少保留 `document_id`、`field_name`、`expected_value`、可選 normalized value、evidence source、source page / bbox、correction version、label version 與 created timestamp。
- Phase 44 不新增 production labeling UI、正式 reviewer RBAC、外部 labeling vendor、batch annotation workflow、layout analysis、table reconstruction 或 production OCR tuning。

## Phase 26 VLM Parser Provider Boundary

Phase 26 的目標是把 parser default 切成 VLM-first demo path：`vlm_invoice` 先從既有 upload metadata 解析 demo-safe image input，再呼叫可設定的 local VLM provider；provider unavailable、timeout、unsupported file、invalid response、missing fields 或 confidence too low 時，才 fallback 到 `deterministic_invoice`。v0.27.1 起 VLM request 也帶 compact OCR context，VLM 欄位結果會嘗試對回 OCR line / bbox。這不改 Phase 25 Agent planner / tool allowlist；Agent 仍只透過 `get_document_fields` 讀取保存後的 parser result。

```text
Admin / Analyst Ingestion Surface
    |
    |-- upload demo-safe image
    |-- run provider-selected OCR
    |-- run parser explicitly
    |
FastAPI Backend Parser Route
    |
    |-- VLM input resolver -> existing data/uploads image path + OCR context
    |-- vlm_invoice adapter -> configurable local VLM provider
    |-- deterministic_invoice fallback
    |
Local JSON Store
    |
    |-- ParserResult parser_source / fallback chain / confidence metadata
    |
Phase 25 Agent
    |
    |-- get_document_fields reads saved ParserResult only
```

Phase 26 contract rules：

- `DOCURAG_VLM_PROVIDER`、`DOCURAG_VLM_BASE_URL`、`DOCURAG_VLM_MODEL`、`DOCURAG_VLM_TIMEOUT_SECONDS` 與 `DOCURAG_VLM_MIN_CONFIDENCE` 定義 provider boundary；`DOCURAG_PARSER_SOURCE=deterministic_invoice` 只作 explicit debug / validation override。
- Input resolver 只支援 `data/uploads/` 內既有 `.png` / `.jpg` / `.jpeg`，並可附帶 OCR text / OCR lines compact context；不做 PDF rendering、multi-page extraction、image preprocessing、layout analysis 或 table reconstruction。
- VLM output 必須正規化成既有 `DocumentFields` / `ExtractedField` / `ParserResult` schema，保留 `parser_source=vlm_invoice`、confidence、source trace、`fallback_chain` 與 `fallback_reason`；欄位 evidence 命中 OCR line 時保存 `source_text` / `source_page` / `source_bbox`，未命中時標示 evidence unmatched / unavailable。
- Fallback 只影響 parser result / parser processing step，不覆蓋 OCR / indexing 狀態，也不觸發 RAG ranking、Qdrant indexing、eval runner、worker、DB 或 permission model。
- `deterministic_invoice` 在 Phase 26 後不再是預設 parser route，只能作為 VLM fallback 或 explicit debug override。

## Phase 27 Aggressive Defaults Boundary

Phase 27 的目標是把「已寫好、已驗證、有 fallback」的進階能力改成 demo 預設，而不是新增 production runtime。

```text
Admin / Analyst Ingestion Surface
    |
    |-- upload -> provider-selected OCR
    |-- best-effort VLM-first parser
    |-- best-effort Qdrant vector indexing
    |
Viewer Chat / Agent search
    |
    |-- default hybrid_rerank retrieval
    |-- keyword evidence fallback
    |-- answer generation fallback
```

Phase 27 default rules：

- `DOCURAG_RAG_RETRIEVAL_PROVIDER=hybrid_rerank` 成為 backend default；`keyword` 只作 debug / validation override。
- `DOCURAG_EMBEDDING_PROVIDER=ollama` 與 `DOCURAG_RERANK_PROVIDER=fastembed` 成為 default adapter selection；兩者不可用時不得讓 `/rag/query` hard fail。
- `POST /documents/{document_id}/index/vector` 仍是同步 API，不代表 worker pipeline；frontend 只是在 OCR 後 best-effort 呼叫。
- OCR 仍是 RAG / vector indexing 的文字層來源；VLM fields 只作 parser structured fields，不在 Phase 27 自動寫成 retrieval chunks。
- Agent planner / tool allowlist 不變；`search_documents` 使用 default RAG provider，但 Agent 不新增任意 tool、SQL、reindex 或 destructive behavior。
- 不新增 PostgreSQL、Redis、NATS、worker、Auth、RBAC、OpenAI API、vLLM、PDF rendering 或 production parser dashboard。

### Phase 27 Vector Source Contract

`27-03` 補上的 source contract 只定義後續 ingestion 邊界，不改 runtime。現有 Qdrant best-effort indexing 主要吃 `ocr_image` chunks，也就是圖片 / 掃描類上傳先由 OCR 產生文字層，再把 OCR chunks 寫入 vector store。

```text
Image upload
    |-- provider-selected OCR
    |-- normalized chunks: source_type=ocr_image, content_source=ocr_image
    |-- manual / best-effort vector indexing

Direct .txt upload
    |-- direct text chunking
    |-- normalized chunks: source_type=text_upload, content_source=text_upload

Text-native PDF
    |-- PDF text extraction with pypdf
    |-- normalized chunks: source_type=pdf_text, content_source=pdf_text

Scanned PDF
    |-- PDF rendering: 34-02 demo-safe page images
    |-- Page OCR: 34-03 provider-selected OCR status / retry
    |-- OCR chunks: source_type=pdf_page_ocr, content_source=pdf_scanned_ocr
```

Normalized vector source metadata must include `document_id`, `filename`, `chunk_id`, `source_type`, `content_source`, optional `page_number`, optional `bbox`, optional `confidence`, `created_at` and reserved future `project_id` / `tenant_id` fields. This keeps Qdrant from becoming permanently coupled to image-only OCR chunks while separating demo-safe scanned PDF OCR from production layout / table understanding.

VLM structured fields remain parser output for Admin / Analyst and Agent `get_document_fields`; they are not automatically converted into retrieval chunks. Field indexing requires a separate policy ticket.

## Phase 35 Indexing Quality Contract

`35-01` is a Markdown-only contract ticket. It defines how Phase 35 should treat chunking strategy, Qdrant payload metadata, filter boundaries, reindex operations and stale vector cleanup. It does not add runtime chunking code, Qdrant index creation, worker execution, eval dashboard logic, OCR changes, parser changes, Agent planner changes or Auth / RBAC behavior changes.

`35-03` implements the first runtime slice for the Qdrant side of this contract. Vector indexing now ensures payload indexes for tenant, project, document and source filters, writes `tenant_id`, `project_id`, `content_source` and `chunk_type` into Qdrant payloads, and can delete stale points for the same document after a successful replacement upsert. Project-level reindex is exposed through the backend API and remains synchronous / demo-safe; it does not introduce a Redis / NATS worker, eval dashboard, rerank algorithm, embedding model selection or LLM generation change.

### Chunking Strategies

| Strategy | Contract | Good fit | Required trace metadata |
|---|---|---|---|
| `fixed_size` | Split normalized text into deterministic windows with bounded overlap. The same input, size and overlap must produce stable `chunk_id` values. | Baseline regression, OCR text, mixed sources with weak document structure, smoke tests. | `chunking_strategy`, `chunking_version`, `chunk_index`, text range, optional token range and overlap size. |
| `semantic` | Split by visible document boundaries such as headings, paragraphs, list blocks, page sections or table-like text blocks, then fall back to `fixed_size` when boundaries are unclear. | Text-native PDFs, reports, contracts and uploaded text where section boundaries improve citation quality. | `chunking_strategy`, `chunking_version`, section title when available, page range and fallback reason when fixed windows are used. |
| `parent_child` | Keep a parent record for larger section / page context and child chunks for retrieval. Retrieval cites child chunks, while answer generation may include the parent context. | Long contracts, policy documents, manuals and cases where small retrieval units need surrounding context. | `chunk_type` (`parent` / `child`), `parent_chunk_id`, child order, parent title or page range and citation child id. |

No strategy may drop the existing source taxonomy from Phase 27 and Phase 28. A chunk created from `ocr_image`, `text_upload`, `pdf_text` or `pdf_page_ocr` must keep its source metadata so citations can still point back to the original document source.

### Qdrant Payload and Filter Boundary

Phase 35 vectors must reserve a Qdrant payload shape that can be filtered by tenant, project, document, source, page and chunk type. Required payload keys are:

- Identity and tenancy: `tenant_id`, `project_id`, `document_id`, `filename`.
- Source trace: `source_type`, `content_source`, `page_number`, optional `bbox`, optional `confidence`.
- Chunk trace: `chunk_id`, `chunk_type`, `chunking_strategy`, `chunking_version`, optional `parent_chunk_id`.
- Index audit: `index_run_id`, `document_revision`, `created_at`, `indexed_at`, optional `stale_at`.

Tenant and project filters are retrieval boundaries, not the source of permission truth. Formal Auth / RBAC remains an API-layer guard; Qdrant queries must still include tenant / project / document filters whenever that context is available, so a future production store does not rely on client-side filtering after retrieval.

### Reindex and Stale Vector Cleanup

`reindex_document` is the document-level operation: it reprocesses one document with an explicit strategy, version and reason, writes a new `index_run_id`, and records created / skipped / failed chunk counts. `reindex_project` is the project-level operation: it schedules or runs the same contract across all visible documents in a project, preserving tenant and project filters.

Stale vector cleanup must be non-destructive to source documents. A new index run should identify previous points by `document_id`, `document_revision`, `chunking_strategy`, `chunking_version` and `index_run_id`, mark replaced points with `stale_at` when supported, then delete or exclude stale vectors only after the replacement run succeeds. Cleanup must never delete document metadata, OCR output, parser fields or source chunks.

Indexing audit metadata must include `index_run_id`, target scope (`document` or `project`), `tenant_id`, `project_id`, optional `document_id`, requested strategy, requested version, requester identifier when available, reason, status, started / finished timestamps, created / replaced / stale / failed counts and fallback or failure reasons.

## Phase 28 Document Source Router Boundary

`28-01` 把 upload 後的處理路徑從「全部先塞進 OCR」改成明確 source router contract。這張票只定義邊界，不改 runtime。

```text
Upload metadata
    |
    |-- image / image content type -> image_ocr
    |       |-- provider-selected OCR
    |       |-- chunks: source_type=ocr_image, content_source=ocr_image
    |
    |-- .txt / text/plain -> text_upload
    |       |-- direct text chunks completed in 28-02
    |       |-- parser / RAG / Qdrant / Agent consume saved chunks
    |       |-- no OCR job and no ocr_mock source
    |
    |-- text-native PDF -> pdf_text
    |       |-- PDF text extraction in 28-03
    |       |-- page_number preserved, bbox nullable
    |
    |-- scanned / empty PDF -> pdf_scanned_pending_ocr
            |-- PDF rendering + OCR pipeline required later
            |-- pending / unsupported until implemented
```

Normalized document text contract 至少包含 `document_id`、`source_type`、`text`、`page_number`、`bbox`、`confidence`、`metadata` 與 `created_at`。`text_upload` 與 `pdf_text` 的 `bbox` / `confidence` 可為 `null`；`ocr_image` 應沿用 OCR line trace。`28-02` 已讓 `.txt` 上傳直接產生 `source_type=text_upload` chunks，OCR status 保持 pending，local indexing 標示 completed；`28-03` 已讓 text-native PDF 直接產生 `source_type=pdf_text` chunks，保留 page number；frontend 對兩者都會跳過 OCR 並顯示對應來源。

本邊界只新增 `pypdf` text extraction，不新增 PDF rendering、scanned PDF OCR、worker、DB schema、正式 auth / RBAC、Redis、NATS 或 deployment 設定。

## Phase 34 Scanned PDF / Production OCR Contract

`34-01` defines the scanned PDF OCR contract. `34-02` adds the demo-safe PDF rendering runtime: `PyMuPDF` renders scanned PDF pages into bounded PNG page images and stores page metadata. `34-03` connects those page images to provider-selected OCR, records page-level status / retry metadata and produces `pdf_page_ocr` chunks. It still does not implement layout analysis, table reconstruction, human correction workflow, frontend route changes, production worker durability or production OCR tuning.

```text
PDF upload
    |
    |-- text-native PDF
    |       |-- source_type=pdf_text
    |       |-- current pypdf text extraction
    |
    |-- scanned PDF
    |       |-- source_type=pdf_scanned_pending_ocr
    |       |-- current 34-02 page image records
    |       |-- current 34-03 page-level OCR blocks
    |       |-- OCR chunks source_type=pdf_page_ocr
    |
    |-- mixed PDF
    |       |-- text pages -> pdf_text chunks
    |       |-- scanned pages -> pdf_mixed_pending_ocr page images
    |       |-- current page-level OCR status
    |       |-- append pdf_page_ocr chunks without dropping pdf_text chunks
    |
    |-- invalid PDF
            |-- no chunks
            |-- failure_reason=pdf_invalid / pdf_encrypted / pdf_render_failed
```

Page image records are page-scoped and stored on `DocumentMetadata.page_images`. Each record keeps `image_id`, `document_id`, `page_number`, `page_status`, image path, width, height, dpi, checksum, OCR text, OCR blocks, OCR attempts, OCR provider, `created_at`, `updated_at`, `source_type`, metadata and optional `failure_reason`. `34-02` writes `rendered` page images for scanned pages; `34-03` updates them to `ocr_running`, `ocr_succeeded` or `ocr_failed` during provider-selected OCR.

OCR blocks must preserve `block_id`, `page_number`, text, bbox, confidence, reading order, provider, language and provider version where available. Missing bbox / confidence stays `null`; the runtime must not invent layout evidence.

Failure and retry are also page-level. Standard failure reasons are `pdf_invalid`, `pdf_encrypted`, `pdf_render_failed`, `page_image_too_large`, `ocr_provider_unavailable`, `ocr_timeout`, `ocr_invalid_output`, `page_empty`, `worker_unavailable` and `unknown_error`. A document becomes ready only when required pages are OCR-succeeded or intentionally skipped because they were text-native.

Handoff rules:

- Parser gets compact OCR text plus OCR blocks after required pages finish.
- Chunks from scanned pages use `source_type=pdf_page_ocr` and `content_source=pdf_scanned_ocr`, with page number and block evidence preserved.
- Vector indexing waits for page-level OCR completion or records partial / skipped pages in metadata.
- Phase 33 worker task status mirrors rendering / OCR progress but does not execute production OCR in this contract ticket.

`34-02` uses `DOCURAG_PDF_RENDER_DPI` and `DOCURAG_PDF_RENDER_MAX_SIDE` to keep local page images bounded. Text-native PDF remains on the `pdf_text` path and does not create page images; invalid / unsupported PDF stores an explicit failure reason. `34-03` executes page image OCR synchronously through the existing provider-selected OCR endpoint; durable async OCR worker execution remains outside this slice.

## Phase 28 Demo Auth Boundary

`28-04` 新增 demo-safe login mode，讓角色差異可以透過前端登入狀態與 backend write API guard 展示。

```text
DOCURAG_AUTH_MODE=demo
    |
    |-- /auth/login -> signed demo bearer token
    |-- /auth/me -> current demo user / role
    |-- /auth/logout -> stateless logout acknowledgement
    |
Document write APIs
    |
    |-- Admin / Analyst -> upload / OCR / parse / vector index allowed
    |-- Viewer -> ingestion write APIs return 403 forbidden
    |-- download -> authenticated users only, all demo roles allowed
```

Demo token payload 只保存 username / role 並用本機 secret 簽章；沒有 refresh token、DB user record、password reset、SSO、OAuth、MFA、Redis session、audit pipeline、organization / project isolation 或 metadata permission filtering。Frontend role gating 只是 UX 呈現，write API guard 仍在 backend dependency 中執行。

## Phase 29 Built-in RAG Eval Boundary

```text
Admin / Analyst 後台「測試RAG」
    |
    |-- POST /eval/rag/built-in
    |
Backend eval wrapper
    |
    |-- load synthetic Chinese invoice fixtures
    |-- fixed hybrid_rerank provider
    |-- fallback-safe keyword evidence path
    |
UI summary
    |
    |-- Hit Rate@K / MRR@K / average latency
    |-- Failure / Fallback
    |-- collapsible failed / fallback cases
```

Boundary rules：

- 不提供 strategy selector；第一版只跑 `hybrid_rerank`。
- Fixture 只測 retrieval evidence 是否被找回，不測 OCR、PDF layout、VLM parser 或 answer quality。
- Runtime unavailable 時必須顯示 fallback state；不得把 keyword fallback 說成完整 vector / rerank 成功。
- Demo auth Viewer 不進入後台測試或 Agent 操作；backend endpoint 仍用 ingestion write guard 擋下 Viewer。
- 不新增 production eval dashboard、DB-backed run history、custom dataset upload、LLM-as-judge、worker 或正式 RBAC。

## Phase 36 Eval Dashboard / Rerank Analysis Contract

`36-01` defines the target contract for a broader RAG quality surface. It upgrades the Phase 29 built-in benchmark language into a dashboard shape. `36-02` adds eval dataset / eval item management for Admin / Analyst. `36-03` adds synchronous strategy comparison runs for managed eval datasets, persists run summaries and case details, and exposes failure cases, fallback cases and rerank analysis in the frontend. It still does not add worker execution, new ranking algorithms, production monitoring trends, answer faithfulness scoring or LLM-as-judge.

Future architecture:

```text
Eval dataset
    |
    |-- eval items with query, expected documents / chunks, tags
    |
Eval run
    |
    |-- one or more strategies: keyword / vector / hybrid / vector_rerank / hybrid_rerank
    |-- same project / tenant guard as document and RAG APIs
    |
Strategy comparison summary
    |
    |-- Hit Rate@K / MRR@K / Recall@K / Precision@K / latency
    |-- failure count / fallback count
    |
Case detail
    |
    |-- retrieved candidates
    |-- expected hit / miss
    |-- fallback and failure reasons
    |
Rerank analysis
    |
    |-- pre-rerank rank / score
    |-- post-rerank rank / score
    |-- final score source and trace metadata coverage
```

Boundary rules:

- Eval dataset / item management is metadata CRUD only; it does not trigger retrieval, rerank, LLM generation, OCR eval or worker execution.
- A dashboard card or table may compare retrieval strategies, but the contract does not tune ranking behavior.
- `failure_count` means expected evidence was not found or the strategy could not produce evaluable output.
- `fallback_count` means the strategy returned a result with fallback metadata, such as vector unavailable or reranker unavailable.
- Rerank analysis reads existing trace metadata (`rerank_score`, `pre_rerank_score`, `rerank_status`, `fallback_state`) and must not call the reranker outside an explicit eval run.
- The first UI surface should remain a diagnostic tool for Admin / Analyst; Viewer access to eval results requires a later ticket.
- LLM-as-judge, answer faithfulness, citation quality scoring, OCR eval and VLM parser accuracy eval remain out of scope.

## Phase 41 RAG Quality Regression / DatasetOps Contract

`41-01` defines how the project should treat RAG quality regression after the Phase 36 eval dashboard work. It is a Markdown-only contract: it does not add backend runtime, frontend UI, CI workflow, database schema, migration, external service, LLM-as-judge or production eval dashboard.

Target evidence flow:

```text
Golden dataset version
    |
    |-- cases with query, expected documents / chunks, expected terms, case tags
    |
Strategy snapshot
    |
    |-- keyword / vector / hybrid / vector_rerank / hybrid_rerank
    |-- chunking strategy, top K, provider availability, fallback policy
    |
Eval run
    |
    |-- Hit Rate@K / MRR@K / Recall@K / latency
    |-- fallback count / failure count / trace metadata coverage
    |
Regression report
    |
    |-- baseline vs current metric delta
    |-- pass / warn / fail regression gate
    |-- failure and fallback reasons for manual review
```

Boundary rules:

- Golden dataset is the stable input contract. Each case should carry `case_version`, `source_document_version`, expected evidence ids, expected terms and tags so later changes can explain why a metric moved.
- Strategy snapshot is required for every eval run. A metric without strategy, chunking, provider availability and fallback metadata is not comparable.
- Regression report compares baseline vs current for Hit Rate@K, MRR@K, Recall@K, latency, fallback count, failure count and trace metadata coverage.
- `regression gate=pass` means metrics stay within tolerance; `warn` means manual review is needed; `fail` means expected evidence quality regressed enough to block a future release candidate.
- Phase 41 keeps answer quality evaluation out of scope. It does not add LLM-as-judge, answer faithfulness, citation quality scoring, human labeling, ranking tuning, default `/rag/query` behavior changes or long-term production trend storage.

## Phase 37 Inference Provider Ops Contract

`37-01` defines the inference provider boundary for LLMOps-facing work. `37-02` adds the first OpenAI-compatible LLM adapter for RAG generation only. It does not start vLLM, add a deployment file, change the VLM parser route, change the Agent planner or remove the current Ollama-first demo path.

Target architecture:

```text
RAG generation / VLM parser / future Agent planner
    |
    |-- inference provider router
          |
          |-- ollama adapter
          |-- openai_compatible adapter
          |-- vllm adapter using OpenAI-compatible HTTP shape
    |
    |-- normalized inference result
          |
          |-- output text / structured payload
          |-- token metrics
          |-- latency / throughput metrics
          |-- fallback and malformed-response metadata
```

Provider boundary:

| Provider | Role | Required fallback behavior |
|---|---|---|
| `ollama` | Current local demo provider for generation and VLM parser spike. | Remains local fallback when compatible endpoints are disabled or unavailable. |
| `openai_compatible` | Implemented in `37-02` for RAG generation through `{base_url}/chat/completions`. | Must be explicitly enabled with `DOCURAG_LLM_PROVIDER=openai_compatible`; unavailable / timeout / malformed response falls back to existing safe path. |
| `vllm` | Optional local serving path exposed through the same OpenAI-compatible `/v1` API. | Must never become the only runtime; `37-03` documents local / Docker serving and benchmark smoke only. |

Metrics boundary:

- `prompt_tokens`, `completion_tokens`, `total_tokens`, `latency_ms`, `tokens_per_second`, `finish_reason`, `provider_request_id`.
- `37-02` maps compatible response `usage.prompt_tokens`, `usage.completion_tokens`, `usage.total_tokens`, `choices[0].finish_reason`, response `id`, measured provider latency and derived throughput into existing RAG citation trace metadata.
- Local serving estimates may include `gpu_memory_estimate_mb` and `kv_cache_estimate_mb`, but estimates must be labeled as estimates unless a later benchmark ticket measures them.
- Metrics must be attached to existing trace metadata or report artifacts; missing metrics stay `null` / unavailable rather than being displayed as `0`.

`37-03` local serving / benchmark boundary:

- vLLM local serving is documented as an optional Docker / GPU path using `vllm/vllm-openai` and the OpenAI-compatible `/v1/chat/completions` shape.
- `scripts/inference-benchmark-smoke.ps1` records latency, prompt tokens, completion tokens, total tokens, derived throughput, KV cache estimate and GPU memory estimate when a compatible endpoint is reachable.
- When vLLM is unavailable, the smoke script writes a skipped report with provider status and fallback guidance to Ollama or the deterministic baseline.
- This does not add multi-GPU serving, production autoscaling, K8s deployment, model registry, prompt changes, ranking changes or a production inference gateway.

Fallback boundary:

- Provider unavailable, timeout, malformed response, rate limit or unsupported modality must be represented as explicit `provider_status` and `fallback_reason`.
- Fallback must not clear OCR results, parser fields, retrieved chunks, eval run results or Agent trace steps.
- Provider routing must not bypass Auth / RBAC guards, project filters, Agent tool allowlists or retrieval source filters.
- `37-01` does not change RAG prompt text, Agent planner behavior, VLM parser schema, ranking algorithm, rerank provider or frontend streaming behavior.

## Phase 42 Inference Gateway / Capacity Planning Contract

`42-01` is a Markdown-only contract ticket. It turns the existing Ollama, OpenAI-compatible and vLLM documentation from Phase 37 into an inference gateway boundary, but does not add provider runtime, streaming API, OpenAI SDK, vLLM server, Docker service or production autoscaling.

Gateway provider domain:

| Provider domain | Runtime meaning | Required boundary |
|---|---|---|
| `ollama` | Current local LLM / VLM / embedding provider and fallback path. | Remains the demo-safe local baseline; Phase 42 does not change prompts, parser behavior or embedding behavior. |
| `openai_compatible` | Existing explicit LLM generation adapter using an OpenAI-compatible chat endpoint. | Requires explicit env selection and must record unavailable / timeout / malformed response fallback. |
| `vllm` | Optional local serving target exposed through the OpenAI-compatible HTTP shape. | Treated as local serving / benchmark evidence, not as the only runtime or a production serving guarantee. |
| `disabled` | Intentional no-provider / unavailable state for validation or fallback. | Must produce explicit skip / fallback metadata instead of pretending a provider succeeded. |

Routing and fallback metadata should be consistent across RAG generation, VLM parser traces, future Agent planner attempts and capacity reports when those paths already expose metadata:

- Provider selection: `selected_provider`, `attempted_providers`, `fallback_target`, `provider_status`, `skip_reason`.
- Request / response metadata: `model`, `provider`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `latency_ms`, `tokens_per_second` / `tokens/sec`, `timeout_seconds`, `fallback_reason`.
- Routing policy: prefer explicit configured provider, preserve Ollama / deterministic safe fallback, and record the full attempted provider chain.
- Retry policy: no automatic retry loop is added in `42-01`; later runtime tickets must bound retries by attempt count, timeout budget and idempotency expectations.
- Provider health and circuit breaker boundary: docs may define health states such as `healthy`, `degraded`, `unavailable` and circuit breaker states such as `closed`, `open`, `half_open`, but `42-01` does not implement a circuit breaker service.

Capacity planning report boundary:

- Report artifacts may compare latency p50 / p95, tokens/sec, context length, concurrency, VRAM estimate, KV cache estimate, TOPS / NPU interpretation, bottleneck notes and provider skip reason.
- Capacity numbers must separate measured local results from estimates. Unknown values stay `null`, `not_measured` or `skipped`; they must not be shown as zero.
- Capacity planning is evidence for interview and local ops reasoning. It is not production autoscaling, multi GPU serving, SLA, paid API key management, secret vault, model registry or cloud capacity guarantee.
- `42-04` records this artifact in `docs/inference-capacity-planning-report.md`; it links Phase 40 hardware evidence, the existing inference benchmark smoke script and Phase 42 gateway provider decisions without running a new long benchmark.

`42-02` runtime metadata notes:

- RAG LLM generation success now records `llm_provider_selected`, `llm_provider_status=completed` and `llm_fallback_target=""`; failure keeps the retrieved chunks fallback and records `llm_provider_status=timeout|unavailable|disabled` plus `llm_fallback_target=retrieved_chunks`.
- VLM-first parser trace records `vlm_provider_selected`, `vlm_provider_status` and `vlm_fallback_target=deterministic_invoice` when provider_unavailable, timeout, invalid response, missing fields or low confidence falls back.
- Vector retrieval records `vector_provider_selected`, `vector_provider_status` and `vector_fallback_target=keyword` when embedding or Qdrant is unavailable; rerank records `rerank_provider_selected`, `rerank_provider_status` and `rerank_fallback_target=original_candidates` when disabled, timeout or failed.
- This is metadata glue only. It does not change provider defaults, start vLLM, add load balancing, add production circuit breaker runtime or make optional providers mandatory.

`42-03` streaming / timeout guardrail runtime notes:

- Ollama and OpenAI-compatible LLM calls remain non-streaming for the demo API path (`stream=false`). This ticket does not add SSE, WebSocket, frontend token streaming or a queue-based scheduler.
- RAG citation trace now exposes `llm_timeout_ms`, `llm_num_predict`, `llm_max_tokens`, `llm_streaming_mode`, `llm_truncated_reason` and `llm_generation_latency_ms` when the path can measure or derive them.
- Timeout failures record `llm_provider_status=timeout`, keep `llm_fallback_target=retrieved_chunks` and preserve the original error in `llm_error`, so a slow provider does not hard fail the demo.
- Truncation is provider-reported only. Unknown truncation state stays empty rather than being inferred from fabricated token counts.

## Phase 39 Deployment / Observability / Fine-tuning Research Contract

`39-01` is a Markdown-only contract for deployment and MLOps-facing evidence. It defines what later Phase 39 tickets may add, but does not add manifests, runtime services, notebooks, dependencies or version changes by itself.

Phase 39 keeps the project honest: it can show deployment shape, traceable logs and research artifacts, but it must not imply production autoscaling, multi-cluster operations or a production training pipeline.

Execution order:

1. `39-01` defines the contract and boundaries.
2. `39-02` may add basic K8s manifests and configuration templates.
3. `39-03` may add observability examples and RAG trace log guidance.
4. `39-04` may add research-only fine-tuning / synthetic data artifacts.
5. `39-05` performs release sync if the Phase forms `v0.39.0`.

K8s baseline scope:

| Artifact | Required content | Boundary |
|---|---|---|
| Deployment | Backend container, frontend static service shape, env wiring examples. | No production rollout strategy, autoscaling policy or multi-cluster deployment. |
| Service | Cluster-internal service examples for backend / frontend. | No cloud load balancer, ingress controller or certificate automation unless a later ticket scopes it. |
| ConfigMap | Non-secret app config examples such as environment, provider selection and API base URL. | Must not contain production secrets or API keys. |
| Secret template | Placeholder keys only, for local documentation and shape validation. | Must not include real secret values, external account credentials or production database URLs. |
| Health probes | Backend `/health` readiness / liveness examples. | Probe examples must not claim production SLOs. |
| Resource requests | Conservative CPU / memory examples for local / demo workloads. | Not capacity planning for production traffic or GPU scheduling. |

`39-02` adds the baseline deployment artifacts under `infra/k8s/`:

- `docurag-baseline.yaml` defines the `docurag` namespace, ConfigMap, Secret template, backend API, frontend, worker placeholder, Qdrant, Redis and NATS manifests.
- `hpa-optional.yaml` is an optional API HPA shape only; it is not backed by production load testing or SLOs.
- The Secret manifest is a template with placeholder values only. It must not contain production secrets, API keys, external account credentials or production database URLs.
- Backend, frontend and worker images use the current `0.38.0` sample tag because Phase 39 release sync is deferred to `39-05`.
- The worker manifest intentionally has no Service because the current worker skeleton does not expose inbound traffic. It remains a placeholder until a later ticket changes the worker runtime.
- Qdrant, Redis and NATS use `emptyDir` demo storage in this baseline, so the manifests do not claim durable production persistence.
- Local validation includes an offline YAML shape check. `kubectl apply --dry-run=client --validate=false` should be run when a Kubernetes context is available; on kubectl versions that still perform API discovery, it will fail before manifest validation if no cluster is configured.

Observability path:

- Phase 39 selects Loki + Grafana as the default local observability path because it matches log aggregation and dashboard evidence with minimal operational weight.
- OpenSearch remains an alternative search-oriented log path, but is not the default track unless a later ticket explicitly changes it.
- API logs should include request id, route, status code, latency, auth mode / role, project id when present and provider fallback metadata.
- Worker logs should include `task_id`, task type, lifecycle status, attempt, trace id, idempotency key and failure reason.
- RAG trace logs should include retrieval provider, top K, fallback state, citation count, visible project / document scope and latency. They should not log raw document text, full prompt bodies, bearer tokens or secrets by default.
- Eval metrics logs should include dataset id, run id, strategy, Hit Rate@K, MRR@K, Recall@K, latency, failure count and fallback count.

`39-03` adds an opt-in JSONL observability exporter and local Loki / Grafana query path:

- `DOCURAG_OBSERVABILITY_LOG_PATH` controls JSONL export. If it is empty, observability export is disabled. If the file cannot be written, the app logs a warning and keeps serving requests.
- Every event uses `schema_version=docurag_observability_v1` and keeps `trace_id`, `request_id`, `organization_id`, `project_id`, `actor_user_id`, `document_id`, `strategy`, `provider`, `latency_ms`, `status` and `error_code`.
- `api_request` events cover route, method, status code and request latency for p95 latency and error-rate queries.
- `rag_trace` events cover `top_k`, citation / retrieved chunk counts, fallback count / reasons, retrieval latency, rerank latency, generation latency, query cache status and rate-limit status. They intentionally do not include raw query text, document text or prompt bodies.
- `eval_metrics` events cover run / dataset identifiers, strategy, Hit Rate@K, MRR@K, Recall@K, average latency, failure count, fallback count and trace metadata count.
- `worker_log` events cover task lifecycle status, task type, topic, idempotency key, attempt, failure reason and error code.
- `infra/observability/` documents the Loki + Grafana opt-in path, Promtail JSON labels and LogQL examples for API p95 latency, API error rate, worker task failures, retrieval / rerank / generation latency, fallback count, Hit Rate and MRR.
- The Docker Compose `observability` profile adds Loki, Promtail and Grafana only when explicitly enabled; it is not required for the baseline backend / frontend demo.

Fine-tuning / synthetic data / embedding tuning research scope:

- Phase 39 may define a research-only SFT / synthetic data / embedding tuning plan using demo-safe sample data and generated examples.
- Research artifacts may include dataset card, prompt template notes, experiment report format, evaluation metric plan or notebook skeleton in a later scoped ticket.
- Research artifacts must not run long training jobs, download large models, change the default runtime model, upload private data, require paid services or claim production model improvement.
- Main OCR, parser, RAG, Agent, Auth / RBAC and inference provider defaults remain unchanged by `39-01`.

`39-04` adds the first research-only artifact pack:

- `fine-tuning/` documents the synthetic data plan, dataset card, notebook skeleton, SFT format, embedding tuning pairs, reranker tuning pairs and evaluation template.
- `sample-data/fine-tuning/` contains small JSONL / CSV examples for invoice, contract and report schema extraction research.
- Evaluation reporting keeps Hit Rate@K, MRR@K, Recall@K, parser field accuracy, sample count, data source and skip reason visible.
- The artifact pack stays disconnected from production runtime and does not add training jobs, dependencies, model downloads, registry upload, deployment automation or provider defaults.

Out of scope for `39-01`:

- No K8s manifests, Helm chart, Docker image change, deployment config runtime or CI deployment workflow.
- No Loki, Grafana, OpenSearch, Prometheus or collector service.
- No production autoscaling, HPA, multi-cluster topology, ingress, cert-manager, service mesh or incident workflow.
- No production training pipeline, fine-tuning notebook, model registry, model artifact, external account, API key or paid-service credential.

## Near-Term Runtime Boundary

目前 runtime 邊界如下：

```text
Browser / PowerShell smoke scripts
    |
FastAPI Backend
    |
Local JSON store and optional local model services
```

這個階段允許 demo-first 進階預設、demo auth mode 與 fallback trace；不得新增 database schema、worker、正式 auth、queue 或 deployment hardening。

Phase 23 只整理 Viewer Chat 與 Admin / Analyst Ingestion 的入口邊界；Phase 28 只新增 demo login 與最小 role gates。若需要真正登入、RBAC、project permission、worker queue 或 database-backed ingestion，必須拆到後續 phase。

## Phase 31 PostgreSQL Boundary

`31-02` 只定義 PostgreSQL boundary、migration policy 與 local JSON fallback / migration path，不新增 schema、migration 檔、repository runtime 或 API 行為。到 v0.29.0 follow-up hardening 為止，demo runtime 仍由 local JSON store、uploaded files、optional Qdrant 與 optional local model services 支撐。

Phase 31 DB domain mapping：

| Current source | Current runtime data | Future DB domain |
|---|---|---|
| `data/documents.json` | document metadata、OCR results、chunks、parser result、processing jobs | `documents`、`document_pages`、`document_chunks`、`extracted_fields`、`processing_jobs` |
| `data/agent_runs.json` | deterministic Agent runs、plan steps、tool calls、citations | `agent_runs`、`agent_steps`、`agent_tool_calls` |
| `sample-data/eval/*.json` / request-time eval output | eval datasets、built-in benchmark fixtures、RAG eval summaries | `eval_datasets`、`eval_items`、`eval_runs`、`eval_run_items` |
| `data/uploads/` | uploaded file artifacts | DB rows should reference file path / checksum metadata; files are not stored as DB bytes in this boundary. |

Migration policy：

- Future runtime migrations should use Alembic after the backend DB stack is introduced by a scoped implementation ticket.
- Migration names should use readable slugs such as `phase31_create_documents_tables` and reference the ticket id / target version in release notes.
- Migration execution requires explicit DB configuration, for example `DATABASE_URL` plus `python -m alembic upgrade head`, only after the dependency and config ticket exists.
- Every migration must include a downgrade path; destructive changes must follow expand / migrate / contract sequencing and require local JSON or DB backup validation.
- Each schema / repository ticket must prove local JSON fallback still works unless that ticket explicitly changes the default.

Local JSON remains the default demo fallback. `31-04` adds opt-in repository selection with `DOCURAG_REPOSITORY_PROVIDER=local_json|postgresql` and `DOCURAG_DATABASE_URL`, plus a local JSON to PostgreSQL migration command. The migration imports existing local JSON data idempotently by stable document id, chunk id and Agent run id. PostgreSQL stores metadata and relational state; Qdrant remains the vector store for embeddings.

`31-03` adds a Markdown-only DB schema contract for Phase 31 core tables: `documents`, `document_pages`, `document_chunks`, `extracted_fields`, `processing_jobs`, `eval_datasets`, `eval_items`, `eval_runs`, `eval_run_items`, `agent_runs`, `agent_steps` and `agent_tool_calls`. The contract preserves nullable `project_id` / future tenant metadata for later filtering, but does not add users, organizations, roles, memberships, migrations, repository code or runtime DB selection.

`31-04` adds `LocalJsonDocumentRepository` and `PostgresDocumentRepository` behind the existing `DocumentStorage` API. The PostgreSQL adapter creates only non-destructive `CREATE TABLE IF NOT EXISTS` tables and uses upsert-based metadata writes for documents, chunks, parser fields, eval runs and Agent runs. The optional dependency is isolated in the `postgres` backend extra; local JSON remains the default and PostgreSQL mode is enabled only when explicitly configured.

## Phase 32 Formal Auth / RBAC / Tenant Boundary Contract

`32-01` defines the formal Auth / RBAC / tenant boundary as a Markdown-only contract. `32-02` adds the PostgreSQL schema foundation and explicit migration command for users, organizations, projects, roles and memberships. Current endpoint runtime remains Phase 28 demo auth until later Phase 32 tickets add backend guards and frontend role surface.

Domain contract:

- User: authenticated human account; persistence and password / token handling are deferred to runtime tickets.
- Organization: top-level tenant boundary. A user without organization membership must not see organization projects.
- Project: workspace boundary for documents, chunks, eval runs, Agent runs and future Qdrant payload filters. Existing nullable `project_id` metadata from Phase 31 is the forward-compatible join point.
- Role: project-scoped permission tier. Supported roles are `viewer`, `analyst` and `admin`.
- Membership: user-to-organization / project relationship with role and active / disabled status.
- Project access: backend-enforced authorization check applied before read or write operations. Frontend role gating is not authoritative.

Role matrix:

| Capability | Viewer | Analyst | Admin |
|---|---:|---:|---:|
| Read own user context | yes | yes | yes |
| List accessible projects | yes | yes | yes |
| Query and download accessible project documents | yes | yes | yes |
| Upload documents | no | yes | yes |
| Run OCR, parser and vector indexing | no | yes | yes |
| Run built-in eval and deterministic Agent tools | no | yes | yes |
| Manage project metadata or memberships | no | no | yes |
| Cross-organization / cross-project access | no | no | no |

API guard policy:

- Read APIs require authenticated project membership and must filter by project access before returning resources.
- Ingestion write APIs require Analyst or Admin for the target project; Viewer receives `403 forbidden`.
- Admin / membership APIs require Admin for the target project or organization.
- Unauthorized / forbidden responses must not leak whether a cross-project resource exists.
- Demo auth remains a local fallback and validation path only; it must not be described as production RBAC.

`32-02` schema foundation:

- `users`: stores username, optional email, display name, password hash, disabled state, auth source and JSON payload.
- `organizations` and `projects`: define the tenant and project workspace boundary that later guards must enforce.
- `roles`: persists canonical `viewer`, `analyst` and `admin` permission payloads from the `32-01` matrix.
- `memberships` and `project_memberships`: persist organization membership and project access rows, including active / disabled status.
- `scripts/migrate-auth-rbac-schema.py` creates the schema with non-destructive `CREATE TABLE IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS` statements and optional demo foundation seed rows.

Completed in `32-03`: endpoint permission guards and cross-project filtering enforcement. Still deferred after `32-03`: production login runtime, JWT refresh rotation, Redis session, SSO, OAuth, MFA, password reset, email verification, audit pipeline and frontend role surface.

`32-03` backend guard runtime:

- `DOCURAG_AUTH_MODE=formal` enables signed bearer token parsing for current user, organization, active project and accessible project ids.
- Write APIs for document upload, OCR, parser, vector indexing, built-in eval and Agent run require Analyst or Admin.
- Read APIs filter document lists, RAG query corpus and Agent search corpus to accessible project ids; document detail, OCR result, fields, download and Agent run lookup deny cross-project access.
- Cross-project denied responses use generic `403 forbidden` details and do not include target document id or project id.
- Demo auth remains available through `DOCURAG_AUTH_MODE=demo`; production login runtime, refresh tokens, Redis session, SSO, OAuth, MFA, audit pipeline and frontend role surface remain deferred.

## Deferred Or Explicitly Optional Components

以下能力是長期目標或 optional local runtime，不屬於目前 production-ready MVP：

- Production VLM / parser pipeline、PDF rendering、image preprocessing、多頁 production OCR pipeline。
- Production indexing worker、自動 queue reindex、DB-backed retrieval management。
- Production eval dashboard trend monitoring、LLM-as-judge、answer faithfulness scoring、citation quality scoring。
- Multi-user tenancy、production login、RBAC、destructive migration、production DB operation。Phase 31 目前已完成 PostgreSQL boundary / schema contract / opt-in repository adapter，不代表 production tenancy、production database operation 或 release sync 已完成。
- Production Redis session rotation、cross-service cache invalidation 與 worker lock runtime；`33-02` 只完成 opt-in demo-safe session cache、query cache 與 rate limit slice。
- Production NATS event bus、durable JetStream consumer、async OCR / parser / indexing / eval worker execution；`33-03` 只完成 NATS helper、worker skeleton 與 task status slice。
- Production autonomous Agent、LLM planner、arbitrary tool runtime 或 destructive tool execution。
- vLLM / OpenAI-compatible serving。
- K8s manifests、deployment hardening、observability runtime、fine-tuning pipeline。`39-01` 只定義 Phase 39 research / deployment / observability contract。

## Design Rules

- 先完成可驗收的最小切片，再擴充 AI pipeline。
- API contract 先保持清楚，不提前建立複雜抽象。
- metadata 欄位要能支援 OCR / RAG / eval trace 狀態，但不在目前 MVP 實作資料庫 schema。
- 每次只依 ticket 修改必要檔案。
- 文件與 TODO 要跟 ticket 狀態同步。
