# DocuRAG AgentOps Frontend

最小 Vue 3 + Vite demo UI，用來檢查 backend health、上傳文件、顯示文件列表、執行 OCR，並用 local RAG chat 查看 deterministic answer、citations 與 retrieved chunks。v0.5.1 搭配公開 sample data、demo seed script 與 API smoke test，讓 GitHub / 面試展示可以快速重跑。v0.6 bridge 保持 UI contract 不變，backend 目前只用 `KeywordRagProvider` 回傳 local keyword RAG 結果。v0.7 的 real OCR spike 已選定 PaddleOCR，backend 已新增 provider-selected OCR endpoint；v0.9 起 provider-selected `/ocr` 預設走 GPU-only PaddleOCR + PP-OCRv4 mobile 中文 / 中英混合模型設定，mock path 仍保留供沒有 real OCR dependency 的環境重跑。

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

v0.9.0 UI 支援：

- `GET /health` 顯示 backend 狀態。
- 首頁只顯示目前版本號。
- `POST /documents/upload` 上傳本機文件。
- 上傳成功後自動刷新 `GET /documents` 文件列表。
- 文件列表顯示 filename、status、OCR status、size、created_at 與 content_type。
- 點選 filename 後呼叫 `GET /documents/{document_id}`，並顯示 metadata JSON。
- 選中文件後可按 `Run Mock Override` 呼叫 `POST /documents/{document_id}/ocr/mock`。
- 選中文件後也可按 `Run Selected OCR` 呼叫 provider-selected `POST /documents/{document_id}/ocr`；backend 預設 provider 是 PaddleOCR PP-OCRv4 mobile 中文 / 中英混合設定，也可用 `DOCURAG_OCR_PROVIDER=mock` 改成 mock。
- OCR client 支援 `GET /documents/{document_id}/ocr` 查詢目前 OCR result。
- OCR result 面板顯示 OCR status、OCR text 與 extracted fields。
- 文件列表與 OCR result 面板顯示 backend `processing` contract 的 indexing、ready 與 latest job 狀態。
- RAG chat 可輸入 query 與 top_k，呼叫 `POST /rag/query`。
- RAG result 面板顯示 deterministic answer、citations、retrieved chunks 與 optional trace metadata，例如 source_type、page_number、bbox、confidence 與 metadata；缺值時前端會保持相容不顯示。

建議 demo query：

```text
payment due date Net 15
```

在 backend 已執行 `scripts/seed-demo-data.ps1` 後，RAG result 預期會引用 `mock-invoice-aurora.txt`，retrieved chunks 會包含 `Invoice number: AUR-2026-051`、`Due date: 2026-06-15` 或 `Payment terms: Net 15` 等公開 demo 文字。

目前 frontend 展示的是 local keyword RAG baseline，不是 embedding、Qdrant、rerank 或真正 LLM。backend v0.6 bridge 只把 `/rag/query` 整理到 `KeywordRagProvider`，並用 `processing`、`processing_jobs` 與 chunk / citation trace contract 顯示 upload / OCR / indexing / job / citation metadata。v0.9 provider-selected OCR 預設走 GPU-only PaddleOCR；若 dependency、Python 版本、CUDA build 或模型不可用，backend 會用清楚錯誤與 processing metadata 呈現，不會靜默 fallback 到 mock。既有 mock OCR UI flow 仍可用 `Run Mock Override` 重跑；這不代表已完成 PDF rendering、image preprocessing 或 production OCR pipeline。
