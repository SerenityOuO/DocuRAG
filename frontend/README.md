# DocuRAG AgentOps Frontend

最小 Vue 3 + Vite demo UI 目前已拆成前台 Viewer Chat 與後台 Admin / Analyst Ingestion 兩個 surface。v0.27.0 起預設先打開後台 Admin / Analyst Ingestion，讓 demo 第一眼呈現上傳、provider-selected OCR、VLM-first parser、Agent trace 與 best-effort Qdrant vector indexing。Viewer Chat 可切換使用，只查詢後端已建立的文件知識庫，並顯示 answer、answer source、retrieval source 與 citation summary。OCR detail、raw JSON、retrieval trace table 與 eval metrics 可由 backend API、smoke scripts 或 CLI 檢查，不屬於 Viewer Chat 主流程；正式知識庫 worker / DB pipeline 尚未實作。backend v0.27.0 預設使用 `hybrid_rerank` RAG / Agent search、Ollama embedding 與 FastEmbed rerank adapter；Ollama embedding、Qdrant 或 reranker 不可用時，UI 會顯示 fallback 狀態。這仍不是 production VLM parser、autonomous Agent dashboard 或正式 RBAC。

## Install

```powershell
cd frontend
npm.cmd install
```

## Run

```powershell
cd frontend
npm.cmd run dev
```

預設網址：

```text
http://localhost:5173
```

## API Base URL

前端會讀取 `VITE_API_BASE_URL`。未設定時預設使用：

```text
http://127.0.0.1:8000
```

PowerShell 設定範例：

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
npm.cmd run dev
```

## Build

```powershell
cd frontend
npm.cmd run build
```

## Demo UI

### Phase 25 Agent Trace Surface

- Admin / Analyst / developer-oriented surface can call `POST /agent/run` with a demo-safe task, document and query.
- The Agent trace surface shows deterministic plan, tool calls, observation, final answer, citations and fallback state.
- Admin / Analyst ingestion is the default demo surface in v0.27.0; Viewer Chat remains available as a separate front surface.
- This is a deterministic tool-use demo surface, not a production autonomous Agent dashboard, RBAC surface, worker runtime or DB-backed tool console.

目前 UI 支援：

- 前台 Viewer Chat：輸入 query 與 top_k，呼叫 `POST /rag/query`，用來查詢已建立的 demo knowledge base。
- 回答結果：顯示 answer、answer source、retrieval source 與簡化引用來源。
- 空知識庫狀態：以 Viewer 角度提示需先由後台知識庫管理流程建立資料，不在前台查詢畫面提供文件上傳或 OCR 操作。
- 後台 Admin / Analyst Ingestion：預設入口，呼叫 `POST /documents/upload` 與 provider-selected `POST /documents/{document_id}/ocr`，顯示 document / OCR / parser / local chunks 狀態；OCR 成功後會 best-effort 執行 `POST /documents/{document_id}/parse` 與 `POST /documents/{document_id}/index/vector`；real OCR 失敗時才提供手動 `POST /documents/{document_id}/ocr/mock` fallback。
- 欄位解析：OCR 完成後可在後台觸發 `POST /documents/{document_id}/parse`，並顯示 parser status、document type、invoice number、vendor、issue date、total amount、currency、confidence 與 source text 摘要；missing fields 會顯示 fallback metadata，詳細 JSON 留給 `GET /documents/{document_id}/fields` 或 API docs。
- Phase 26 parser source comparison：API response 會透過 `parser_source`、`trace_metadata.fallback_chain`、`trace_metadata.fallback_reason`、`trace_metadata.confidence_summary` 與 source input metadata 區分 `vlm_invoice` 與 `deterministic_invoice`；frontend 仍只呈現 demo-friendly structured fields 摘要，不新增 production parser comparison dashboard。
- 後端健康：只顯示簡短連線狀態與版本，不顯示 raw health JSON。
- 工程細節：OCR text、extracted fields、document list、metadata JSON、retrieved chunks、trace metadata 與 eval metrics 改由 backend API、`scripts/demo-smoke-test.ps1`、`scripts/retrieval-eval-smoke.ps1` 或 API docs 檢查，不放在 frontend 主畫面；正式知識庫 ingestion / indexing pipeline 尚未實作。
- backend 預設嘗試 Ollama LLM provider；generation 成功時 answer source 顯示 `ollama/qwen3.5:4b`，Ollama 不可用時顯示 `LLM unavailable fallback`，若以 `DOCURAG_LLM_PROVIDER=` 明確關閉則顯示 `確定性基準回答`。
- backend 預設使用 `hybrid_rerank`；retrieval source 可能顯示 `hybrid_rerank`、`hybrid_rerank 備援：vector_unavailable`、`hybrid_rerank 備援：reranker_unavailable`、`vector/qdrant` 或舊 keyword baseline override。

建議面試前先 seed demo knowledge base，讓前台客服聊天一打開就能問：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
```

建議 demo query：

```text
payment due date Net 15
```

在 backend 已執行 `scripts/seed-demo-data.ps1` 後，RAG result 預期會引用 `mock-invoice-aurora.txt`；詳細 chunks 與 trace 可用 smoke script 或 API response 檢查。

目前 frontend 預設展示的是 Admin / Analyst ingestion + default `hybrid_rerank` RAG / Agent search + default-on Ollama answer generation path。backend 會優先嘗試 Ollama embedding、Qdrant 與 FastEmbed rerank；若 runtime 不可用，會 fallback 到 keyword retrieval 並保留 trace。未覆寫 `DOCURAG_LLM_PROVIDER` 時會把 retrieved chunks 與 query 交給 Ollama `qwen3.5:4b` 產生回答；Ollama 不可用時會明確 fallback，若要回到 deterministic baseline 可設定 `DOCURAG_LLM_PROVIDER=`。OCR 是 backend ingestion layer：上傳後由 backend provider-selected GPU-only PaddleOCR 產生 OCR result 與 local chunks，前端只呈現角色入口、狀態與結果。若 dependency、Python 版本、CUDA build 或模型不可用，backend 會用清楚錯誤與 processing metadata 呈現，後台 ingestion flow 才顯示手動 mock fallback，不會靜默 fallback 到 mock。Parser 在 Phase 26 起預設為 VLM-first provider spike，success path 標記 `vlm_invoice`，provider unavailable、unsupported file 或 invalid response 才 fallback 到 `deterministic_invoice`；這不代表已完成 production VLM parser、PDF rendering、image preprocessing、production OCR pipeline、streaming UI 或 production indexing worker。

## Release Status

- v0.20.0: Interview MVP Packaging 已完成；frontend build、local demo view 檢查、README demo media 與 release 文件同步已完成。
- v0.21.0: Real GPU OCR Interview Demo Path 已完成；frontend upload 預設走 provider-selected real GPU OCR，mock OCR 只作手動 fallback。
- v0.22.0: RAG Query Hardening 已完成；frontend contract 不變，backend keyword query normalization 支援中文 demo 問法命中。
- v0.23.0: Viewer Chat / Admin Ingestion Role Split 已完成；Viewer Chat-only 預設入口與後台知識庫管理 surface 已完成，版本與文件同步已完成。
- v0.24.0: VLM / Parser Minimal MVP 已完成；後台可觸發 deterministic invoice parser，顯示 structured fields 摘要、missing metadata 與 parser status，版本與文件同步已完成。
- v0.25.0: Agent Tool-use Minimal MVP 已完成；後台 Agent trace surface 可顯示 deterministic plan、allowlisted tool calls、observations、final answer、citations 與 fallback state，版本與文件同步已完成。
- v0.26.0: Real VLM Parser Provider Spike 已完成；後台 structured fields surface 可顯示 `vlm_invoice` / `deterministic_invoice` parser source 與 fallback metadata，Agent trace 仍只透過 `get_document_fields` 讀取保存結果。
- v0.27.0: Aggressive Demo Defaults 已完成；後台預設入口、OCR 後 best-effort parser + vector indexing、default `hybrid_rerank` retrieval source / fallback 顯示與版本文件同步已完成。
