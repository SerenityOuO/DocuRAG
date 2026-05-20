# DocuRAG AgentOps

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台 side project，目標是呈現企業級文件解析、RAG 評估、citation trace 與 AgentOps 的端到端產品思維。

專案的長期方向來自 `goal.md`：文件上傳後可被解析、檢索、問答、評估，並能用 Agent 工具完成多步分析任務。第一版不會一次接滿 OCR、RAG、Qdrant、Redis、NATS、vLLM 與 K8s，而是先用小 ticket 建立可逐步驗收的工程骨架。

## Project Goal

DocuRAG AgentOps 要展示三件事：

- 文件智能平台的產品流程：從文件進入系統，到 metadata、解析結果、問答與評估。
- RAG 工程能力：不只回答問題，也保留 citation、trace 與後續評估指標。
- 可維護的 AI application 架構：讓 backend、frontend、docs、tasks 與 infra 的責任邊界清楚。

## MVP Scope

MVP 採用 incremental thin slice，先跑通產品故事與 API 邊界：

- Phase 00：建立文件、任務票與 repo 開發規範。
- Phase 01：建立最小 backend healthcheck 與 Docker 啟動邊界。
- Phase 02：建立文件上傳 API 與文件 metadata schema 的基礎。
- v0.3.0：把文件上傳升級成本機存檔、local JSON metadata、文件列表與詳情查詢。

MVP 初期可以使用 fixture 或最小資料結構，不要求真正 AI pipeline。以下能力保留為後續階段：

- 真正 OCR / VLM parser。
- 真正 embeddings / Qdrant indexing。
- 真正 Redis session / NATS worker。
- 真正 rerank / RAG generation。
- vLLM / Ollama serving。
- production-grade K8s deployment。

## Development Direction

本專案採用 ticket-first 工作流：

1. 每次只處理一張 `tasks/` 底下的小 ticket。
2. 每張 ticket 都要能在一次 Codex 工作階段完成。
3. 每張 ticket 完成後應可單獨 commit。
4. 實作前先讀 ticket 的 Goal、Scope、Out of Scope、Acceptance Criteria 與 Validation。
5. 不把後續階段的 OCR、RAG、infra 或 auth 複雜度提前塞進當前 ticket。

## Repository Structure

目前 MVP v0.3 使用以下結構：

```text
DocuRAG/
├── README.md
├── .github/
│   └── workflows/
│       └── backend-ci.yml
├── AGENTS.md
├── TODO.md
├── goal.md
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   └── LOCAL_DEV_SETUP.md
├── data/
│   └── uploads/
│       └── .gitkeep
├── backend/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── README.md
│   └── package.json
├── infra/
│   └── docker-compose.yml
├── scripts/
│   ├── check-dev-env.ps1
│   └── test-backend.ps1
└── tasks/
    ├── _TEMPLATE.md
    ├── phase-00-bootstrap/
    ├── phase-01-backend-bootstrap/
    └── phase-02-document-foundation/
```

OCR、RAG、Qdrant、Redis、NATS、vLLM、登入權限與資料庫 schema 仍保留為後續 ticket。

## Local Run

先檢查本機 Python / Docker 狀態：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-dev-env.ps1
```

如果 PowerShell execution policy 已允許本機腳本，也可以直接執行：

```powershell
.\scripts\check-dev-env.ps1
```

安裝 backend 依賴：

```powershell
cd backend
py -3 -m pip install -e ".[dev]"
```

啟動 backend：

```powershell
cd backend
py -3 -m uvicorn app.main:app --reload
```

驗證 healthcheck：

```powershell
curl http://127.0.0.1:8000/health
```

FastAPI docs UI：

```text
http://127.0.0.1:8000/docs
```

驗證文件上傳：

```powershell
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@sample.pdf"
```

查詢文件列表：

```powershell
curl http://127.0.0.1:8000/documents
```

查詢文件詳情：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}
```

啟動 frontend：

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend UI：

```text
http://localhost:5173
```

執行測試：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1
```

## Docker

單獨 build backend image：

```powershell
docker build -t docurag-backend ./backend
```

使用 Compose 啟動 backend：

```powershell
docker compose -f infra/docker-compose.yml up --build
```

背景啟動並驗證 healthcheck：

```powershell
docker compose -f infra/docker-compose.yml up -d
curl http://127.0.0.1:8000/health
docker compose -f infra/docker-compose.yml down
```

## v0.2.0 Demo UI

v0.2.0 加入最小 Vue 3 + Vite frontend、backend CORS、GitHub Actions backend CI，並完成 Docker build / Docker Compose 驗證。

Demo 操作流程：

1. 啟動 backend：`cd backend` 後執行 `py -3 -m uvicorn app.main:app --reload`。
2. 開啟 FastAPI docs：`http://127.0.0.1:8000/docs`。
3. 啟動 frontend：`cd frontend` 後執行 `npm.cmd run dev`。
4. 開啟 frontend：`http://localhost:5173`。
5. 確認頁面顯示 backend health。
6. 選擇本機檔案並上傳，確認 upload result 與 API response JSON。

## v0.3.0 Document Local Storage

v0.3.0 將 `POST /documents/upload` 從 stub 升級為本機儲存 MVP：

- 上傳檔案會存到 `data/uploads/`。
- 文件 metadata 會寫到 `data/documents.json`。
- `GET /documents` 依 `created_at` 由新到舊回傳文件列表。
- `GET /documents/{document_id}` 回傳單一文件詳情，找不到時回傳 404。
- `GET /documents/{document_id}/download` 可下載已保存的原始檔。
- 前端會顯示文件列表，點選文件可查看 metadata JSON。

`data/uploads/*` 與 `data/documents.json` 是 runtime files，不會提交到 Git；只保留 `data/uploads/.gitkeep` 讓資料夾存在。

Demo 操作流程：

1. 啟動 backend：`cd backend` 後執行 `py -3 -m uvicorn app.main:app --reload`。
2. 上傳文件：`curl -X POST http://127.0.0.1:8000/documents/upload -F "file=@sample.pdf"`。
3. 查詢列表：`curl http://127.0.0.1:8000/documents`。
4. 查詢詳情：`curl http://127.0.0.1:8000/documents/{document_id}`。
5. 啟動 frontend：`cd frontend` 後執行 `npm.cmd run dev`。
6. 開啟 `http://localhost:5173`，確認 health、upload result、文件列表與 metadata JSON。

## Documentation

- `goal.md`：完整產品構想與長期目標。
- `docs/PRD.md`：依 `goal.md` 收斂後的 MVP 產品需求。
- `docs/ARCHITECTURE.md`：MVP 架構與明確延後的元件。
- `docs/ROADMAP.md`：Phase 00 到 Phase 02 的開發路線。
- `TODO.md`：目前階段 checklist。
- `tasks/`：可單次完成、可單獨 commit 的任務票。

## Current Status

目前完成 MVP v0.3.0 Document Local Storage：

- `GET /health` 回傳 service、status、version。
- `POST /documents/upload` 可接收 `UploadFile`，保存原始檔並回傳 document metadata。
- `GET /documents` 回傳 local metadata 文件列表。
- `GET /documents/{document_id}` 回傳文件詳情。
- backend 已允許 local frontend CORS origin。
- backend 可用 pytest 驗證。
- backend 可用 Dockerfile / Compose 啟動。
- frontend 可顯示 backend health、選擇檔案、呼叫 upload API、刷新文件列表並查看 metadata JSON。
- GitHub Actions Backend CI 已建立。

尚未實作 OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限或資料庫 schema。

本機驗證狀態請見 `docs/LOCAL_DEV_SETUP.md`。目前 backend pytest、frontend build、Docker build、Docker Compose healthcheck 與 Compose upload API 均已納入 v0.3.0 驗證流程。

## Release Status

- v0.0: repo structure、docs、tasks 已完成。
- v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- v0.2.0: Demo UI、backend CORS、Backend CI、Docker build / Compose 驗證已完成。
- v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI、Docker Compose upload 驗證已完成。
