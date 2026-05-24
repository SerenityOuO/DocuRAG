# MVP Architecture

本文件描述 DocuRAG AgentOps 目前的受控 MVP 架構。到 v0.24.0 為止，專案已完成 backend / frontend demo、provider-selected OCR、local RAG、citation trace、retrieval eval runner、optional vector / rerank / hybrid / `hybrid_rerank` eval strategy、Viewer Chat / Admin Ingestion role split，以及 deterministic parser MVP。Phase 25 先固定 Agent Tool-use contract，但不代表已新增 autonomous Agent、auth / RBAC、worker 或 DB runtime。

## MVP Shape

```text
Viewer Chat Surface
    |
    |-- RAG answer / answer source / retrieval source / citations
    |
Admin / Analyst Ingestion Surface
    |
    |-- upload / provider-selected OCR / processing status
    |-- OCR result / local chunks / metadata debug links
    |-- Phase 24 parser result: OCR text -> structured fields
    |-- Phase 25 Agent contract: deterministic plan -> allowlisted tools -> trace
    |
FastAPI Backend
    |
    |-- health / document API / OCR API / RAG API / parse / fields API
    |-- future Agent run API
    |-- manual vector indexing API
    |-- retrieval eval runner CLI
    |
Local Data Store
    |
    |-- uploads / metadata JSON / OCR results / chunks / parser results / future Agent runs
    |
Optional Local AI Runtime
    |
    |-- PaddleOCR GPU provider
    |-- Ollama generation / embedding
    |-- Qdrant vector collection
    |-- FastEmbed rerank adapter
```

MVP 的預設路徑保持 local keyword RAG baseline，確保沒有 optional runtime 時也能重跑 demo。vector retrieval、rerank、hybrid 與 `hybrid_rerank` 都必須 explicit opt-in；`hybrid_rerank` 目前只在 retrieval eval runner 裡使用，不接 default `/rag/query` 或 frontend chat route。

Phase 23 的 role split 是 demo surface 與產品敘事邊界，不是正式權限系統。Viewer Chat 不提供上傳或 OCR 操作；Admin / Analyst ingestion surface 可以呼叫既有 backend upload / OCR API，並在 Phase 24 後顯示 deterministic parser structured fields。Phase 25 Agent surface 仍屬於 Admin / Analyst / developer-oriented demo，不進入 Viewer Chat 主流程。

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

## Near-Term Runtime Boundary

Phase 20 的 runtime 邊界如下：

```text
Browser / PowerShell smoke scripts
    |
FastAPI Backend
    |
Local JSON store and optional local model services
```

這個階段只整理 demo readiness、sample / eval coverage、README media 與 final validation。不得新增 backend API、frontend route、database schema、worker、auth、queue 或 deployment 設定。

Phase 23 只整理 Viewer Chat 與 Admin / Analyst Ingestion 的入口邊界。若需要真正登入、RBAC、project permission、worker queue 或 database-backed ingestion，必須拆到後續 phase。

## Deferred Or Explicitly Optional Components

以下能力是長期目標或 optional local runtime，不屬於目前 production-ready MVP：

- VLM / parser pipeline、PDF rendering、image preprocessing、多頁 production OCR pipeline。
- Default-on vector retrieval、default-on rerank、default-on hybrid / `hybrid_rerank` chat path。
- Production eval dashboard、strategy comparison UI、LLM-as-judge、answer faithfulness scoring、citation quality scoring。
- PostgreSQL schema、multi-user tenancy、login、RBAC。
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
