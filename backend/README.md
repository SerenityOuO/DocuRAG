# Backend

DocuRAG AgentOps backend MVP v0.5.1 是最小 FastAPI 服務，提供 healthcheck、文件本機上傳、metadata 保存、文件列表、文件詳情、OCR mock API、local RAG query API、demo seed script 與 API smoke test，並允許 local frontend 透過 CORS 呼叫。v0.6 bridge 先整理 provider contract，目前 OCR 預設仍是 `MockOcrProvider`，RAG 只接 `KeywordRagProvider`。v0.7 的 real OCR spike 已選定 PaddleOCR，並新增 provider-selected OCR endpoint；此階段不接資料庫、OpenAI API、Ollama、vLLM、embedding、Qdrant、rerank、Redis、NATS 或登入權限。

## Install

```powershell
cd backend
py -3 -m pip install -e ".[dev]"
```

## Run

```powershell
cd backend
py -3 -m uvicorn app.main:app --reload
```

Healthcheck：

```powershell
curl http://127.0.0.1:8000/health
```

Upload：

```powershell
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@sample-data/documents/mock-invoice-aurora.txt"
```

Document list：

```powershell
curl http://127.0.0.1:8000/documents
```

Document detail：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}
```

Document download：

```powershell
curl -OJ http://127.0.0.1:8000/documents/{document_id}/download
```

Run mock OCR：

```powershell
curl -X POST http://127.0.0.1:8000/documents/{document_id}/ocr/mock
```

Run provider-selected OCR：

```powershell
curl -X POST http://127.0.0.1:8000/documents/{document_id}/ocr
```

OCR result：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}/ocr
```

Phase 07 provider decision：

- 07-01 選定 `PaddleOCR` 作為第一個 real OCR spike provider。
- 07-02 已新增 provider-selected `POST /documents/{document_id}/ocr`；既有 `POST /documents/{document_id}/ocr/mock` 保持相容。
- 使用 `DOCURAG_OCR_PROVIDER=mock|paddleocr` 選擇 provider，預設為 `mock`。
- PaddleOCR adapter 採 lazy import，讓未安裝 real OCR dependency 的環境仍可跑 mock demo。
- real provider 不可用時不靜默 fallback 到 mock；real endpoint 應回傳清楚錯誤，並更新 processing status 與 processing job metadata。
- real OCR trace output 會正規化到 `OcrResult.lines`，再映射到 chunk page、bbox、confidence、metadata 與 RAG citation trace metadata。
- mock path 仍是預設與 demo-safe path。

安裝 real OCR optional dependency：

```powershell
cd backend
py -3 -m pip install -e ".[dev,real-ocr]"
```

Docker real OCR build 可用 build arg 開啟，預設不安裝 PaddleOCR：

```powershell
docker build --build-arg DOCURAG_INSTALL_REAL_OCR=true -t docurag-backend-real-ocr ./backend
```

Local RAG query：

```powershell
curl -X POST http://127.0.0.1:8000/rag/query `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"invoice\",\"top_k\":3}"
```

## Local Storage

上傳 API 會將原始檔案保存到 repo root 的 `data/uploads/`，並將 metadata 寫入 `data/documents.json`。`filename` 會先安全化，避免 `../` 或 Windows path separator 造成 path traversal。

OCR mock API 會透過 `MockOcrProvider` 產生 deterministic OCR result，再由 `DocumentStorage` 將 OCR status、text、extracted fields、updated timestamp 與 local chunks 寫回同一份 `data/documents.json`。未執行 OCR 的文件會回傳 `pending` OCR status。

document metadata 會包含 `processing` contract，明確記錄 `upload`、`ocr`、`indexing`、`ready`、`failed_reason` 與 `updated_at`。upload 完成後 OCR / indexing 會保持 pending；mock OCR 成功後 OCR 與 indexing 會標記 completed 並進入 ready；provider 回傳 failed 時會保存 failed_reason，但不啟動 background worker 或 queue。

document metadata 也會保存 `processing_jobs` history 與 `latest_job` summary。同步 upload 會記錄 completed upload job；mock OCR 成功會記錄 completed OCR 與 local indexing job；provider failed 會記錄 failed OCR job。這些 job metadata 只是 contract，不代表已引入 worker、queue、Redis 或 NATS。

v0.5.1 chunks 由 OCR mock text 產生，每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。v0.6 chunk / citation schema 另外補齊 optional `page_number`、`bbox`、`confidence`、`source_type`、chunk `metadata` 與 citation `trace_metadata` 欄位；mock OCR chunk 只填 `source_type=ocr_mock` 與 metadata safe default，不產生真正 OCR bbox 或 confidence。v0.7 real OCR output 先正規化到 `OcrResult.lines`，再將 line-level page、bbox、confidence 與 metadata 寫入 `DocumentChunk`，讓 citations 與 retrieved chunks 不依賴 PaddleOCR 私有格式。`POST /rag/query` 透過 `KeywordRagProvider` 做本機 keyword retrieval，並用 deterministic template 回傳 answer、citations 與 retrieved chunks。對 `text/plain`、`.txt`、`.md`、`.csv` sample，OCR mock 會把上傳文字納入 deterministic mock OCR text，方便 demo query 引用具體欄位；這不是 embedding、Qdrant、rerank 或 LLM。

可用環境變數覆寫資料目錄：

```powershell
$env:DOCURAG_DATA_DIR="C:/tmp/docurag-data"
```

runtime 檔案不會提交到 Git：

- `data/uploads/*`
- `data/documents.json`

repo 只保留 `data/uploads/.gitkeep` 作為資料夾 placeholder。

## Test

從 repo root 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1
```

或在 Python 環境已準備好後手動執行：

```powershell
cd backend
py -3 -m pytest
```

## Demo Scripts

先啟動 backend，再從 repo root 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
```

`demo-smoke-test.ps1` 會驗證 `/health`、upload、OCR mock 與 `/rag/query`。`seed-demo-data.ps1` 會上傳 `sample-data/documents/mock-invoice-aurora.txt`、執行 OCR mock、查詢 `payment due date Net 15`，並輸出 answer、citations、retrieved chunks。

## Docker

```powershell
docker build -t docurag-backend ./backend
docker run --rm -p 8000:8000 docurag-backend
```

或使用 repo 內的 Compose：

```powershell
docker compose -f infra/docker-compose.yml up --build
```

背景啟動後驗證：

```powershell
docker compose -f infra/docker-compose.yml up -d
curl http://127.0.0.1:8000/health
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
docker compose -f infra/docker-compose.yml down
```

## Environment Check

從 repo root 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1
```

如果 Python 或 Docker 不可用，依 `docs/LOCAL_DEV_SETUP.md` 修復本機工具後再重跑測試。

## Release Status

- v0.1.0: FastAPI backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- Python: `scripts/test-backend.ps1` 可透過 `pip.exe` 反推實際 `python.exe` 並建立/使用 `.venv`。
- v0.2.0: backend CORS、Docker image build、Compose build 與 Compose healthcheck 已納入驗證。
- v0.3.0: document local storage、metadata JSON、list/detail/download API 與 Compose upload 驗證已完成。
- v0.4.0: OCR mock API、OCR result persistence、pytest、Docker build 與 Compose OCR mock API 驗證已完成。
- v0.5.0: local chunking、keyword retrieval、RAG answer API、pytest、Docker build 與 Compose RAG API 驗證已完成。
- v0.5.1: demo sample data、seed script、API smoke test、pytest、Docker build 與 Compose demo 驗證已完成。
- v0.6.0: Bridge Contracts、OCR provider interface、RAG provider interface、processing status、chunk citation schema 與 processing job contract 已完成。
