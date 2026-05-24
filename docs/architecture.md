# MVP Architecture

本文件描述 DocuRAG AgentOps 目前的受控 MVP 架構。到 v0.23.0 為止，專案已完成 backend / frontend demo、provider-selected OCR、local RAG、citation trace、retrieval eval runner、optional vector / rerank / hybrid / `hybrid_rerank` eval strategy，以及 Viewer Chat / Admin Ingestion role split。Phase 23 固定產品表面邊界：Viewer Chat 與 Admin / Analyst Ingestion 必須分開表達，但不代表已新增 auth / RBAC。

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
    |-- Phase 24 parser contract: OCR text -> structured fields
    |
FastAPI Backend
    |
    |-- health / document API / OCR API / RAG API
    |-- future parse / fields API
    |-- manual vector indexing API
    |-- retrieval eval runner CLI
    |
Local Data Store
    |
    |-- uploads / metadata JSON / OCR results / chunks / future parser results
    |
Optional Local AI Runtime
    |
    |-- PaddleOCR GPU provider
    |-- Ollama generation / embedding
    |-- Qdrant vector collection
    |-- FastEmbed rerank adapter
```

MVP 的預設路徑保持 local keyword RAG baseline，確保沒有 optional runtime 時也能重跑 demo。vector retrieval、rerank、hybrid 與 `hybrid_rerank` 都必須 explicit opt-in；`hybrid_rerank` 目前只在 retrieval eval runner 裡使用，不接 default `/rag/query` 或 frontend chat route。

Phase 23 的 role split 是 demo surface 與產品敘事邊界，不是正式權限系統。Viewer Chat 不提供上傳或 OCR 操作；Admin / Analyst ingestion surface 可以呼叫既有 backend upload / OCR API，但仍使用 local JSON、provider-selected OCR 與 local chunks，不包含 VLM parser、worker、DB 或 production indexing。

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
- Agent tool-use runtime。
- vLLM / OpenAI-compatible serving。
- K8s manifests and deployment hardening。

## Design Rules

- 先完成可驗收的最小切片，再擴充 AI pipeline。
- API contract 先保持清楚，不提前建立複雜抽象。
- metadata 欄位要能支援 OCR / RAG / eval trace 狀態，但不在目前 MVP 實作資料庫 schema。
- 每次只依 ticket 修改必要檔案。
- 文件與 TODO 要跟 ticket 狀態同步。
