# DocuRAG AgentOps Frontend

最小 Vue 3 + Vite demo UI，只暴露兩個使用者可見入口：客服問答與文件上傳。OCR、chunking、indexing、document list、raw JSON、retrieval trace table 與 eval metrics 都留在 backend API、smoke scripts 或 CLI，不在 frontend 主畫面攤開。v0.5.1 搭配公開 sample data、demo seed script 與 API smoke test，讓 GitHub / 面試展示可以快速重跑。v0.6 bridge 保持 UI contract 不變，backend 以 `KeywordRagProvider` 維持 keyword retrieval 與 citation contract。v0.7 的 real OCR spike 已選定 PaddleOCR，backend 已新增 provider-selected OCR endpoint；v0.9 起 provider-selected `/ocr` 預設走 GPU-only PaddleOCR + PP-OCRv4 mobile 中文 / 中英混合模型設定，mock path 仍保留供沒有 real OCR dependency 的環境重跑。v0.10.0 會在 RAG answer 顯示 `deterministic baseline`、`ollama/qwen3.5:4b` 或 LLM fallback source；v0.11.0 額外顯示 `keyword baseline`、`vector/qdrant` 或 `vector unavailable fallback` retrieval source；v0.12.0 optional vector demo 改為 smoke script 先手動 indexing 再查詢；v0.13.0 retrieval evaluation baseline 由 CLI / smoke script 輸出 metrics；v0.15.0 optional `vector_rerank` eval 仍由 CLI / smoke script 輸出 metrics 與 rerank metadata；v0.16.0 optional `hybrid` eval 也由 CLI / smoke script 輸出 metrics 與 hybrid metadata；v0.19.0 optional `hybrid_rerank` trace 仍由 CLI / smoke script 輸出，frontend 沒有新增 live eval dashboard 或 chat route。v0.20.1 frontend patch 把展示入口收斂為 minimal chat / upload，不新增 frontend route 或 production eval dashboard。

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

- 客服問答：輸入 query 與 top_k，呼叫 `POST /rag/query`。
- 回答結果：顯示 answer、answer source、retrieval source 與簡化引用來源。
- 文件上傳：呼叫 `POST /documents/upload`，再呼叫既有 `POST /documents/{document_id}/ocr/mock` 完成 demo-safe backend ingestion。
- 後端健康：只顯示簡短連線狀態與版本，不顯示 raw health JSON。
- 工程細節：OCR text、extracted fields、document list、metadata JSON、retrieved chunks、trace metadata 與 eval metrics 改由 backend API、`scripts/demo-smoke-test.ps1`、`scripts/retrieval-eval-smoke.ps1` 或 API docs 檢查，不放在 frontend 主畫面。
- backend 未啟用 LLM provider 時，answer source 顯示 `確定性基準回答`；設定 `DOCURAG_LLM_PROVIDER=ollama` 且 generation 成功時顯示 `ollama/qwen3.5:4b`。
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

目前 frontend 預設展示的是 local keyword RAG baseline，不是 default-on vector retrieval、default-on rerank、default-on hybrid retrieval、default-on `hybrid_rerank`、eval dashboard 或 streaming LLM UI。backend 只在 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector` 且 document 已透過 manual indexing API 寫入 Qdrant 後，才會讓 vector retrieval 查詢 Qdrant；失敗會 fallback 到 keyword retrieval。`vector_rerank`、`hybrid` 與 `hybrid_rerank` 目前只接入 CLI eval runner。只在 `DOCURAG_LLM_PROVIDER=ollama` 時把 retrieved chunks 與 query 交給 Ollama `qwen3.5:4b` 產生回答。v0.9 provider-selected OCR 預設走 GPU-only PaddleOCR；若 dependency、Python 版本、CUDA build 或模型不可用，backend 會用清楚錯誤與 processing metadata 呈現，不會靜默 fallback 到 mock。frontend upload 目前使用 mock OCR endpoint 做 demo-safe ingestion；這不代表已完成 PDF rendering、image preprocessing、production OCR pipeline、`/rag/query` hybrid search 或 streaming。

## Release Status

- v0.20.0: Interview MVP Packaging 已完成；frontend build、local demo view 檢查、README demo media 與 release 文件同步已完成。
