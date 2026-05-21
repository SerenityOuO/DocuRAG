# Backend

DocuRAG AgentOps backend MVP v0.5.1 是最小 FastAPI 服務，提供 healthcheck、文件本機上傳、metadata 保存、文件列表、文件詳情、OCR mock API、local RAG query API、demo seed script 與 API smoke test，並允許 local frontend 透過 CORS 呼叫。v0.6 bridge 先整理 OCR provider contract，目前只接 `MockOcrProvider`。此階段不接資料庫、真正 OCR engine、OpenAI API、Ollama、vLLM、embedding、Qdrant、Redis、NATS 或登入權限。

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

OCR result：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}/ocr
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

v0.5.1 chunks 由 OCR mock text 產生，每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。`POST /rag/query` 只做本機 keyword retrieval，並用 deterministic template 回傳 answer、citations 與 retrieved chunks。對 `text/plain`、`.txt`、`.md`、`.csv` sample，OCR mock 會把上傳文字納入 deterministic OCR mock text，方便 demo query 引用具體欄位；這不是真正 OCR、embedding 或 LLM。

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
- v0.6.0: 06-01 OCR provider interface bridge 已完成；其餘 bridge tickets 待執行。
