# API Draft

此文件先定義 MVP API 邊界，實作時可依 ticket 逐步補齊。

## System

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |

## Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Demo login |
| POST | `/auth/logout` | Logout |
| GET | `/auth/me` | Current user |

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
| POST | `/documents/{document_id}/parse` | Run the MVP parser for an OCR-completed document |
| GET | `/documents/{document_id}/chunks` | Document chunks |
| POST | `/documents/{document_id}/index/vector` | Manually index document chunks into Qdrant when embedding / Qdrant runtime is explicitly enabled |

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

## Phase 24 Parser Contract Draft

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

VLM provider 必須回傳 JSON object，並由 adapter 正規化成既有 Phase 24 schema，不新增平行欄位 schema：

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
- `source_text` 可來自 VLM response trace、OCR text 或 normalized field label；沒有來源時可為 `null` 並以 `fallback_reason` 說明。
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
- The default `ollama` provider uses the local HTTP `/api/generate` shape with `stream=false` and image base64; `DOCURAG_VLM_PROVIDER=fake` is a built-in demo / smoke stub and is not a production VLM runtime.
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
