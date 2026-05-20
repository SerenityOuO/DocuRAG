# Backend

DocuRAG AgentOps backend MVP v0.1 是最小 FastAPI 服務，提供 healthcheck 與文件上傳 API stub。此階段不接資料庫、OCR、RAG、Qdrant、Redis、NATS、vLLM 或登入權限。

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

Upload stub：

```powershell
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@sample.pdf"
```

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

## Docker

```powershell
docker build -t docurag-backend ./backend
docker run --rm -p 8000:8000 docurag-backend
```

或使用 repo 內的 Compose：

```powershell
docker compose -f infra/docker-compose.yml up --build
```

## Environment Check

從 repo root 執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1
```

如果 Python 或 Docker 不可用，依 `docs/LOCAL_DEV_SETUP.md` 修復本機工具後再重跑測試。
