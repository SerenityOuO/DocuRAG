# MVP Architecture

本文件描述 DocuRAG AgentOps 目前的受控 MVP 架構。到 v0.29.0 為止，專案已完成 backend / frontend demo、provider-selected OCR、citation trace、retrieval eval runner、built-in RAG eval admin API、vector / rerank / hybrid / `hybrid_rerank` retrieval building blocks、Viewer Chat / Admin Ingestion role split、deterministic Agent tool-use trace、VLM-first parser provider spike、OCR / VLM evidence alignment、aggressive demo defaults、`.txt` direct ingestion、text-native PDF extraction、demo auth mode 與後台「測試RAG」surface。Phase 27 把 RAG / Agent search default 切成 `hybrid_rerank`，並讓 frontend 後台 OCR 後 best-effort 執行 parser 與 vector indexing；v0.27.1 補上 VLM image + OCR context 與欄位 evidence mapping；v0.28.0 補上 first-class `text_upload` / `pdf_text` sources 與 demo role gates；v0.29.0 讓 Admin / Analyst 可執行固定 `hybrid_rerank` 的內建中文發票 retrieval benchmark。這不代表已新增 production VLM parser、正式 auth / RBAC、worker、DB runtime、production eval dashboard 或 scanned PDF OCR。

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
    |-- Phase 25 Agent contract: deterministic plan -> allowlisted tools -> trace
    |
FastAPI Backend
    |
    |-- demo auth API / role guard dependencies
    |-- health / document API / OCR API / RAG API / parse / fields API
    |-- Agent run / lookup API
    |-- manual vector indexing API
    |-- built-in RAG eval API / retrieval eval runner CLI
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

Future scanned PDF
    |-- PDF rendering required
    |-- OCR pipeline required
    |-- current state: source_type=pdf_scanned_pending_ocr
```

Normalized vector source metadata must include `document_id`, `filename`, `chunk_id`, `source_type`, `content_source`, optional `page_number`, optional `bbox`, optional `confidence`, `created_at` and reserved future `project_id` / `tenant_id` fields. This keeps Qdrant from becoming permanently coupled to OCR-only chunks while avoiding a false claim that scanned PDF runtime is already complete.

VLM structured fields remain parser output for Admin / Analyst and Agent `get_document_fields`; they are not automatically converted into retrieval chunks. Field indexing requires a separate policy ticket.

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
- Production eval dashboard、strategy comparison UI、LLM-as-judge、answer faithfulness scoring、citation quality scoring。
- Multi-user tenancy、production login、RBAC、destructive migration、production DB operation。Phase 31 目前已完成 PostgreSQL boundary / schema contract / opt-in repository adapter，不代表 production tenancy、production database operation 或 release sync 已完成。
- Redis session、cache、rate limit。
- NATS event bus。
- Production autonomous Agent、LLM planner、arbitrary tool runtime 或 destructive tool execution。
- vLLM / OpenAI-compatible serving。
- K8s manifests and deployment hardening。

## Design Rules

- 先完成可驗收的最小切片，再擴充 AI pipeline。
- API contract 先保持清楚，不提前建立複雜抽象。
- metadata 欄位要能支援 OCR / RAG / eval trace 狀態，但不在目前 MVP 實作資料庫 schema。
- 每次只依 ticket 修改必要檔案。
- 文件與 TODO 要跟 ticket 狀態同步。
