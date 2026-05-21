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
- v0.4.0：建立 OCR mock pipeline，保存 mock OCR 結果並在 UI 顯示 status、text 與 extracted fields。
- v0.5.0：使用 OCR mock text 建立 local RAG baseline，提供 chunking、keyword retrieval、deterministic answer API 與簡易 Chat UI。
- v0.5.1：補強 GitHub / 面試展示流程，加入公開 sample data、demo seed script、API smoke test 與 5 分鐘 demo 指令。

MVP 初期可以使用 fixture 或最小資料結構，不要求真正 AI pipeline。以下能力保留為後續階段：

- 真正 OCR / VLM parser。
- 真正 embeddings / Qdrant indexing。
- 真正 Redis session / NATS worker。
- 真正 rerank / LLM-based RAG generation。
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

目前 MVP v0.5.1 使用以下結構：

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
├── sample-data/
│   └── documents/
│       ├── mock-invoice-aurora.txt
│       └── mock-contract-support.txt
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
│   ├── demo-smoke-test.ps1
│   ├── seed-demo-data.ps1
│   └── test-backend.ps1
└── tasks/
    ├── _TEMPLATE.md
    ├── phase-00-bootstrap/
    ├── phase-01-backend-bootstrap/
    ├── phase-02-document-foundation/
    ├── phase-03-ocr-mock/
    └── phase-05-rag-baseline/
```

真正 OCR engine、embedding、Qdrant、Redis、NATS、vLLM、登入權限與資料庫 schema 仍保留為後續 ticket。v0.5.1 只提供 deterministic mock OCR text、local keyword retrieval 與 template answer；不是 embedding/Qdrant/LLM RAG。

## 5-Minute Demo v0.5.1

這段流程適合 GitHub README 或面試現場快速展示 upload -> OCR mock -> local RAG -> citations。範例資料位於 `sample-data/documents/`，內容皆為虛構公開資料。

Terminal 1 啟動 backend：

```powershell
cd backend
py -3 -m pip install -e ".[dev]"
py -3 -m uvicorn app.main:app --reload
```

Terminal 2 執行 API smoke test 與 demo seed：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
```

`seed-demo-data.ps1` 會自動上傳 `sample-data/documents/mock-invoice-aurora.txt`、執行 OCR mock、查詢 local RAG，並輸出 `answer`、`citations` 與 `retrieved_chunks`。

範例問題：

```text
payment due date Net 15
```

預期結果會引用 `mock-invoice-aurora.txt` 的 OCR mock chunk，並在 retrieved chunks 看到 `Invoice number: AUR-2026-051`、`Due date: 2026-06-15`、`Payment terms: Net 15` 等公開 demo 文字。

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

Docker demo：

```powershell
docker compose -f infra/docker-compose.yml up -d --build
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed-demo-data.ps1
docker compose -f infra/docker-compose.yml down
```

目前 retrieval 是 local keyword RAG baseline：只用 OCR mock text 產生 chunks 並做關鍵字比對，不使用 embedding、Qdrant、rerank、OpenAI API、Ollama、vLLM 或真正 LLM。

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
  -F "file=@sample-data/documents/mock-invoice-aurora.txt"
```

查詢文件列表：

```powershell
curl http://127.0.0.1:8000/documents
```

查詢文件詳情：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}
```

執行 mock OCR：

```powershell
curl -X POST http://127.0.0.1:8000/documents/{document_id}/ocr/mock
```

查詢 OCR 結果：

```powershell
curl http://127.0.0.1:8000/documents/{document_id}/ocr
```

執行 local RAG 查詢：

```powershell
curl -X POST http://127.0.0.1:8000/rag/query `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"invoice\",\"top_k\":3}"
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

## v0.4.0 OCR Mock Pipeline

v0.4.0 加入可驗證的 mock OCR pipeline，不接 PaddleOCR、Tesseract、VLM 或任何真正 OCR engine：

- `POST /documents/{document_id}/ocr/mock` 會對既有文件產生 deterministic mock OCR text 與 extracted fields。
- `GET /documents/{document_id}/ocr` 可讀取 OCR result；未執行 OCR 的文件會回傳 `pending`。
- OCR result 會寫入 `data/documents.json` 內對應 document metadata。
- OCR result 包含 status、text、extracted fields 與 updated timestamp。
- frontend 可對選中文件按 `Run Mock OCR`，並顯示 OCR status、OCR text 與 extracted fields。

Demo 操作流程：

1. 啟動 backend：`cd backend` 後執行 `py -3 -m uvicorn app.main:app --reload`。
2. 上傳文件：`curl -X POST http://127.0.0.1:8000/documents/upload -F "file=@sample.pdf"`。
3. 執行 mock OCR：`curl -X POST http://127.0.0.1:8000/documents/{document_id}/ocr/mock`。
4. 查詢 OCR 結果：`curl http://127.0.0.1:8000/documents/{document_id}/ocr`。
5. 啟動 frontend：`cd frontend` 後執行 `npm.cmd run dev`。
6. 開啟 `http://localhost:5173`，選擇文件後按 `Run Mock OCR`，確認 OCR status、text 與 extracted fields。

## v0.5.0 Local RAG Baseline

v0.5.0 使用 v0.4.0 的 OCR mock text 作為知識來源，建立第一版本機 RAG baseline，不接真正 LLM、OpenAI API、Ollama、vLLM、embedding、Qdrant 或 rerank：

- `POST /documents/{document_id}/ocr/mock` 完成後會從 OCR text 產生 chunks，並寫入 `data/documents.json`。
- 每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。
- `POST /rag/query` 接收 `query` 與 `top_k`，以 local keyword retrieval 從 chunks 找出 matched chunks。
- RAG response 包含 deterministic `answer`、`citations` 與 `retrieved_chunks`。
- citations 會指出 `document_id`、`filename` 與 `chunk_id`。
- frontend 新增 RAG chat 區，可輸入 query 並顯示 answer、citations 與 retrieved chunks。

Demo 操作流程：

1. 啟動 backend：`cd backend` 後執行 `py -3 -m uvicorn app.main:app --reload`。
2. 上傳文件並執行 mock OCR。
3. 查詢 RAG：`curl -X POST http://127.0.0.1:8000/rag/query -H "Content-Type: application/json" -d "{\"query\":\"invoice\",\"top_k\":3}"`。
4. 啟動 frontend：`cd frontend` 後執行 `npm.cmd run dev`。
5. 開啟 `http://localhost:5173`，在 RAG chat 輸入問題，確認 answer、citations 與 retrieved chunks。

## v0.5.1 Demo Hardening

v0.5.1 補強 demo 可重跑性與 GitHub 可讀性，不新增 Qdrant、embedding、rerank 或真正 LLM：

- `sample-data/documents/` 提供 2 份公開虛構文字樣本。
- `scripts/demo-smoke-test.ps1` 可重跑驗證 `/health`、upload、OCR mock 與 `/rag/query`。
- `scripts/seed-demo-data.ps1` 可上傳 invoice sample、執行 OCR mock、執行範例 RAG query，並輸出 answer、citations、retrieved chunks。
- OCR mock 對 text sample 會把上傳文字納入 deterministic mock OCR text，讓 local keyword RAG 能引用具體 demo 欄位。
- `/health` 回傳 version `0.5.1`。

## Documentation

- `goal.md`：完整產品構想與長期目標。
- `docs/PRD.md`：依 `goal.md` 收斂後的 MVP 產品需求。
- `docs/ARCHITECTURE.md`：MVP 架構與明確延後的元件。
- `docs/ROADMAP.md`：Phase 00 到 v0.5.1 的開發路線。
- `TODO.md`：目前階段 checklist。
- `tasks/`：可單次完成、可單獨 commit 的任務票。

## Current Status

目前完成 MVP v0.5.1 Demo Hardening：

- `GET /health` 回傳 service、status、version。
- `POST /documents/upload` 可接收 `UploadFile`，保存原始檔並回傳 document metadata。
- `GET /documents` 回傳 local metadata 文件列表。
- `GET /documents/{document_id}` 回傳文件詳情。
- `POST /documents/{document_id}/ocr/mock` 會產生並保存 mock OCR result。
- `GET /documents/{document_id}/ocr` 會回傳 OCR status、text、extracted fields 與 updated timestamp。
- OCR mock 完成後會產生並保存 local chunks。
- `POST /rag/query` 會用 local keyword retrieval 回傳 deterministic answer、citations 與 retrieved chunks。
- backend 已允許 local frontend CORS origin。
- backend 可用 pytest 驗證。
- backend 可用 Dockerfile / Compose 啟動。
- frontend 可顯示 backend health、選擇檔案、呼叫 upload API、刷新文件列表、執行 Run Mock OCR、查看 OCR 結果，並用 RAG chat 查詢 answer 與 citations。
- GitHub Actions Backend CI 已建立。
- demo seed script 與 API smoke test 已建立，可用公開 sample data 重跑 demo。

尚未實作真正 OCR engine、embedding、Qdrant、Redis、NATS、vLLM、登入、權限或資料庫 schema。

本機驗證狀態請見 `docs/LOCAL_DEV_SETUP.md`。目前 backend pytest、frontend build、Docker build、Docker Compose healthcheck、Compose upload API、Compose OCR mock API、Compose RAG API、demo smoke test 與 demo seed script 均已納入 v0.5.1 驗證流程。

## Release Status

- v0.0: repo structure、docs、tasks 已完成。
- v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- v0.2.0: Demo UI、backend CORS、Backend CI、Docker build / Compose 驗證已完成。
- v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI、Docker Compose upload 驗證已完成。
- v0.4.0: OCR Mock Pipeline、OCR result persistence、frontend OCR UI、Docker Compose OCR mock API 驗證已完成。
- v0.5.0: Local RAG Baseline、chunking、keyword retrieval、RAG answer API、frontend Chat UI 與 Docker Compose RAG API 驗證已完成。
- v0.5.1: Demo Hardening、公開 sample data、demo seed script、API smoke test、5 分鐘 demo flow 與 Docker Compose demo 驗證已完成。
