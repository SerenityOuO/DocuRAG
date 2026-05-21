# DocuRAG AgentOps Frontend

最小 Vue 3 + Vite demo UI，用來檢查 backend health、上傳文件、顯示文件列表、執行 mock OCR，並用 local RAG chat 查看 deterministic answer、citations 與 retrieved chunks。v0.5.1 搭配公開 sample data、demo seed script 與 API smoke test，讓 GitHub / 面試展示可以快速重跑。v0.6 bridge 保持 UI contract 不變，backend 目前只用 `KeywordRagProvider` 回傳 local keyword RAG 結果。

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

v0.5.1 UI 支援：

- `GET /health` 顯示 backend 狀態。
- `POST /documents/upload` 上傳本機文件。
- 上傳成功後自動刷新 `GET /documents` 文件列表。
- 文件列表顯示 filename、status、OCR status、size、created_at 與 content_type。
- 點選 filename 後呼叫 `GET /documents/{document_id}`，並顯示 metadata JSON。
- 選中文件後可按 `Run Mock OCR` 呼叫 `POST /documents/{document_id}/ocr/mock`。
- OCR client 支援 `GET /documents/{document_id}/ocr` 查詢目前 OCR result。
- OCR result 面板顯示 OCR status、OCR text 與 extracted fields。
- 文件列表與 OCR result 面板顯示 backend `processing` contract 的 indexing、ready 與 latest job 狀態。
- RAG chat 可輸入 query 與 top_k，呼叫 `POST /rag/query`。
- RAG result 面板顯示 deterministic answer、citations、retrieved chunks 與 optional trace metadata，例如 source_type、page_number 與 confidence；缺值時前端會保持相容不顯示。

建議 demo query：

```text
payment due date Net 15
```

在 backend 已執行 `scripts/seed-demo-data.ps1` 後，RAG result 預期會引用 `mock-invoice-aurora.txt`，retrieved chunks 會包含 `Invoice number: AUR-2026-051`、`Due date: 2026-06-15` 或 `Payment terms: Net 15` 等公開 demo 文字。

目前 frontend 展示的是 local keyword RAG baseline，不是 embedding、Qdrant、rerank 或真正 LLM。backend v0.6 bridge 只把 `/rag/query` 整理到 `KeywordRagProvider`，並用 `processing`、`processing_jobs` 與 chunk / citation trace contract 顯示 upload / OCR / indexing / job / citation metadata；真正 OCR / embedding / LLM provider 會留給後續 ticket。
