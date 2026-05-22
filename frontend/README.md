# DocuRAG AgentOps Frontend

最小 Vue 3 + Vite demo UI，用來檢查 backend health、上傳文件、顯示文件列表、執行 OCR，並用 RAG chat 查看 answer、answer source、retrieval source、citations 與 retrieved chunks。v0.5.1 搭配公開 sample data、demo seed script 與 API smoke test，讓 GitHub / 面試展示可以快速重跑。v0.6 bridge 保持 UI contract 不變，backend 以 `KeywordRagProvider` 維持 keyword retrieval 與 citation contract。v0.7 的 real OCR spike 已選定 PaddleOCR，backend 已新增 provider-selected OCR endpoint；v0.9 起 provider-selected `/ocr` 預設走 GPU-only PaddleOCR + PP-OCRv4 mobile 中文 / 中英混合模型設定，mock path 仍保留供沒有 real OCR dependency 的環境重跑。v0.10.0 會在 RAG answer 顯示 `deterministic baseline`、`ollama/qwen3.5:4b` 或 LLM fallback source；v0.11.0 額外顯示 `keyword baseline`、`vector/qdrant` 或 `vector unavailable fallback` retrieval source；v0.12.0 optional vector demo 改為 smoke script 先手動 indexing 再查詢；v0.13.0 retrieval evaluation baseline 由 CLI / smoke script 輸出 metrics；v0.15.0 optional `vector_rerank` eval 仍由 CLI / smoke script 輸出 metrics 與 rerank metadata；v0.16.0 optional `hybrid` eval 也由 CLI / smoke script 輸出 metrics 與 hybrid metadata，不做 frontend eval dashboard。

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

v0.16.0 UI 支援：

- `GET /health` 顯示 backend 狀態。
- 首頁只顯示目前版本號。
- `POST /documents/upload` 上傳本機文件。
- 上傳成功後自動刷新 `GET /documents` 文件列表。
- 文件列表顯示 filename、status、OCR status、size、created_at 與 content_type。
- 點選 filename 後呼叫 `GET /documents/{document_id}`，並顯示 metadata JSON。
- 選中文件後可按 `Run Mock Override` 呼叫 `POST /documents/{document_id}/ocr/mock`。
- 選中文件後也可按 `Run Selected OCR` 呼叫 provider-selected `POST /documents/{document_id}/ocr`；backend 預設 provider 是 PaddleOCR PP-OCRv4 mobile 中文 / 中英混合設定，並使用 startup-preloaded provider / engine，也可用 `DOCURAG_OCR_PROVIDER=mock` 改成 mock。
- OCR client 支援 `GET /documents/{document_id}/ocr` 查詢目前 OCR result。
- OCR result 面板顯示 OCR status、OCR text 與 extracted fields；v0.9.1 會直接呈現 `timing_engine_preload_ms`、`timing_inference_ms`、`timing_normalization_ms`、`timing_total_ms`、`use_angle_cls=false` 等 backend metadata。
- 文件列表與 OCR result 面板顯示 backend `processing` contract 的 indexing、ready 與 latest job 狀態。
- RAG chat 可輸入 query 與 top_k，呼叫 `POST /rag/query`。
- RAG result 面板顯示 answer、answer source、retrieval source、citations、retrieved chunks 與 optional trace metadata，例如 source_type、page_number、bbox、confidence、vector fallback 與 metadata；缺值時前端會保持相容不顯示。
- Retrieval evaluation metrics、optional `vector_rerank` trace metadata 與 optional `hybrid` trace metadata 由 `scripts/retrieval-eval-smoke.ps1` 輸出，不在 v0.16.0 frontend 建立 eval dashboard。
- backend 未啟用 LLM provider 時，answer source 顯示 `deterministic baseline`；設定 `DOCURAG_LLM_PROVIDER=ollama` 且 generation 成功時顯示 `ollama/qwen3.5:4b`；LLM failure fallback 會顯示 `LLM unavailable fallback`。
- backend 未啟用 vector retrieval 時，retrieval source 顯示 `keyword baseline`；設定 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector` 且 Qdrant search 成功時顯示 `vector/qdrant`；embedding 或 Qdrant unavailable fallback 會顯示 `vector unavailable fallback`。

建議 demo query：

```text
payment due date Net 15
```

在 backend 已執行 `scripts/seed-demo-data.ps1` 後，RAG result 預期會引用 `mock-invoice-aurora.txt`，retrieved chunks 會包含 `Invoice number: AUR-2026-051`、`Due date: 2026-06-15` 或 `Payment terms: Net 15` 等公開 demo 文字。

目前 frontend 預設展示的是 local keyword RAG baseline，不是 default-on vector retrieval、default-on rerank、default-on hybrid retrieval、eval dashboard 或 streaming LLM UI。backend v0.16.0 只在 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector` 且 document 已透過 manual indexing API 寫入 Qdrant 後，才會讓 vector retrieval 查詢 Qdrant；失敗會 fallback 到 keyword retrieval。`vector_rerank` 與 `hybrid` 目前只接入 CLI eval runner，不改 frontend UI。只在 `DOCURAG_LLM_PROVIDER=ollama` 時把 retrieved chunks 與 query 交給 Ollama `qwen3.5:4b` 產生回答。v0.9 provider-selected OCR 預設走 GPU-only PaddleOCR；若 dependency、Python 版本、CUDA build 或模型不可用，backend 會用清楚錯誤與 processing metadata 呈現，不會靜默 fallback 到 mock。既有 mock OCR UI flow 仍可用 `Run Mock Override` 重跑；這不代表已完成 PDF rendering、image preprocessing、production OCR pipeline、`/rag/query` hybrid search 或 streaming。
