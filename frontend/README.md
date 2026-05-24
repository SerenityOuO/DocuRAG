# DocuRAG AgentOps Frontend

最小 Vue 3 + Vite demo UI 目前預設入口已收斂為前台 Viewer Chat：只查詢後端已建立的文件知識庫，並顯示 answer、answer source、retrieval source 與 citation summary。後台 Admin / Analyst Ingestion 會在後續 Phase 23 ticket 承接文件上傳、provider-selected OCR、處理狀態與 local chunks / metadata 檢查。OCR detail、document list、raw JSON、retrieval trace table 與 eval metrics 可由 backend API、smoke scripts 或 CLI 檢查，不屬於 Viewer Chat 主流程；正式知識庫 ingestion / indexing pipeline 尚未實作。v0.5.1 搭配公開 sample data、demo seed script 與 API smoke test，讓 GitHub / 面試展示可以快速重跑。v0.6 bridge 保持 UI contract 不變，backend 以 `KeywordRagProvider` 維持 keyword retrieval 與 citation contract。v0.7 的 real OCR spike 已選定 PaddleOCR，backend 已新增 provider-selected OCR endpoint；v0.9 起 provider-selected `/ocr` 預設走 GPU-only PaddleOCR + PP-OCRv4 mobile 中文 / 中英混合模型設定，mock path 仍保留供沒有 real OCR dependency 的環境重跑。v0.10.0 會在 RAG answer 顯示 `deterministic baseline`、`ollama/qwen3.5:4b` 或 LLM fallback source；v0.11.0 額外顯示 `keyword baseline`、`vector/qdrant` 或 `vector unavailable fallback` retrieval source；v0.12.0 optional vector demo 改為 smoke script 先手動 indexing 再查詢；v0.13.0 retrieval evaluation baseline 由 CLI / smoke script 輸出 metrics；v0.15.0 optional `vector_rerank` eval 仍由 CLI / smoke script 輸出 metrics 與 rerank metadata；v0.16.0 optional `hybrid` eval 也由 CLI / smoke script 輸出 metrics 與 hybrid metadata；v0.19.0 optional `hybrid_rerank` trace 仍由 CLI / smoke script 輸出，frontend 沒有新增 live eval dashboard 或 chat route。v0.21.0 backend upload + OCR demo path 預設呼叫 provider-selected real GPU OCR，失敗時才顯示手動 mock OCR fallback button；Phase 23 後這些動作應歸入 Admin / Analyst ingestion surface，不是 Viewer Chat 主線。v0.22.0 backend keyword query normalization 可讓「付款期限是什麼？」這類中文 query 命中英文 payment terms chunks，frontend API contract 不變。

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

目前 UI 支援：

- 前台 Viewer Chat：輸入 query 與 top_k，呼叫 `POST /rag/query`，用來查詢已建立的 demo knowledge base。
- 回答結果：顯示 answer、answer source、retrieval source 與簡化引用來源。
- 空知識庫狀態：以 Viewer 角度提示需先由後台知識庫管理流程建立資料，不在前台查詢畫面提供文件上傳或 OCR 操作。
- 後端健康：只顯示簡短連線狀態與版本，不顯示 raw health JSON。
- 工程細節：OCR text、extracted fields、document list、metadata JSON、retrieved chunks、trace metadata 與 eval metrics 改由 backend API、`scripts/demo-smoke-test.ps1`、`scripts/retrieval-eval-smoke.ps1` 或 API docs 檢查，不放在 frontend 主畫面；正式知識庫 ingestion / indexing pipeline 尚未實作。
- backend 預設嘗試 Ollama LLM provider；generation 成功時 answer source 顯示 `ollama/qwen3.5:4b`，Ollama 不可用時顯示 `LLM unavailable fallback`，若以 `DOCURAG_LLM_PROVIDER=` 明確關閉則顯示 `確定性基準回答`。
- backend 未啟用 vector retrieval 時，retrieval source 顯示 `關鍵字基準檢索`；設定 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector` 且 Qdrant search 成功時顯示 `vector/qdrant`。

建議面試前先 seed demo knowledge base，讓前台客服聊天一打開就能問：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
```

建議 demo query：

```text
payment due date Net 15
```

在 backend 已執行 `scripts/seed-demo-data.ps1` 後，RAG result 預期會引用 `mock-invoice-aurora.txt`；詳細 chunks 與 trace 可用 smoke script 或 API response 檢查。

目前 frontend 預設展示的是 local keyword retrieval + default-on Ollama answer generation path，不是 default-on vector retrieval、default-on rerank、default-on hybrid retrieval、default-on `hybrid_rerank`、eval dashboard 或 streaming LLM UI。backend 只在 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector` 且 document 已透過 manual indexing API 寫入 Qdrant 後，才會讓 vector retrieval 查詢 Qdrant；失敗會 fallback 到 keyword retrieval。`vector_rerank`、`hybrid` 與 `hybrid_rerank` 目前只接入 CLI eval runner。未覆寫 `DOCURAG_LLM_PROVIDER` 時會把 retrieved chunks 與 query 交給 Ollama `qwen3.5:4b` 產生回答；Ollama 不可用時會明確 fallback，若要回到 deterministic baseline 可設定 `DOCURAG_LLM_PROVIDER=`。OCR 是 backend ingestion layer：上傳後由 backend provider-selected GPU-only PaddleOCR 產生 OCR result 與 local chunks，前端只呈現角色入口、狀態與結果。若 dependency、Python 版本、CUDA build 或模型不可用，backend 會用清楚錯誤與 processing metadata 呈現，後台 ingestion flow 才顯示手動 mock fallback，不會靜默 fallback 到 mock。這不代表已完成 PDF rendering、image preprocessing、production OCR pipeline、`/rag/query` hybrid search 或 streaming。

## Release Status

- v0.20.0: Interview MVP Packaging 已完成；frontend build、local demo view 檢查、README demo media 與 release 文件同步已完成。
- v0.21.0: Real GPU OCR Interview Demo Path 已完成；frontend upload 預設走 provider-selected real GPU OCR，mock OCR 只作手動 fallback。
- v0.22.0: RAG Query Hardening 已完成；frontend contract 不變，backend keyword query normalization 支援中文 demo 問法命中。
- v0.23.0: Viewer Chat / Admin Ingestion Role Split backlog 已建立；Viewer Chat-only 預設入口已完成，後續 ticket 會建立後台知識庫管理 surface。
