# DocuRAG AgentOps

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台 side project，用來呈現企業級文件上傳、OCR、local RAG、citation trace 與 AgentOps 產品思維。

目前主線已完成 local document workflow、provider-selected PaddleOCR OCR flow、PP-OCRv4 mobile 中文 / 中英混合模型設定、mock OCR override、local keyword RAG baseline、frontend demo UI，以及可重跑的本機與 Docker backend 環境。這仍是受控 MVP，不是 production OCR / RAG 平台。

## Project Goal

DocuRAG AgentOps 要展示三件事：

- 文件智能平台的產品流程：文件上傳後可保存 metadata、執行 OCR、產生 chunks，並在 UI 中查看處理狀態。
- RAG 工程能力：回答問題時保留 citations、retrieved chunks 與 trace metadata。
- 可維護的 AI application 架構：backend、frontend、docs、tasks、infra 與 sample data 的責任邊界清楚。

## Current Scope

目前最新主線包含：

- FastAPI backend，提供 healthcheck、文件上傳、文件列表、文件詳情、OCR result 與 RAG query API。
- Local JSON metadata store，保存 document metadata、OCR result、chunks、processing status 與 processing job metadata。
- Provider-selected OCR endpoint：`POST /documents/{document_id}/ocr` 預設走 PaddleOCR。
- Mock OCR override：`POST /documents/{document_id}/ocr/mock` 可在沒有 real OCR runtime 時重跑 demo-safe flow。
- OCR line normalization，將 OCR text、page、bbox、confidence 與 metadata 映射到 chunks 與 citations。
- PaddleOCR 預設固定 `lang=ch`、`ocr_version=PP-OCRv4`、`PP-OCRv4_mobile_det` / `PP-OCRv4_mobile_rec`，並保留 model dir env override。
- Local keyword RAG baseline，回傳 deterministic answer、citations 與 retrieved chunks。
- Vue 3 + Vite frontend，可操作 upload、document list/detail、selected OCR、mock override、OCR result 與 RAG chat。
- Python 3.12 backend runtime；real OCR 只支援 PaddlePaddle GPU / CUDA runtime，dependency 收斂在 `backend[real-ocr]` optional extra。
- Dockerfile / Docker Compose backend runtime，real OCR GPU dependency 可透過 build arg 開啟。

目前仍刻意不實作：

- PDF rendering、image preprocessing、版面分析、多頁文件處理或 OCR accuracy tuning。
- Embedding、Qdrant、rerank、LLM generation、OpenAI API、Ollama 或 vLLM。
- Redis、NATS、async worker、queue、PostgreSQL、資料庫 schema、登入、權限或 RBAC。
- Production-grade K8s deployment。

## Local Run

使用 Python 3.12 啟動 backend：

```powershell
cd backend
py -3.12 -m pip install "paddlepaddle-gpu==3.3.0" -i https://www.paddlepaddle.org.cn/packages/stable/cu129/
py -3.12 -m pip install -e ".[dev,real-ocr]"
py -3.12 -m uvicorn app.main:app --reload
```

Backend API：

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

使用 Node.js / npm 啟動 frontend：

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend UI：

```text
http://localhost:5173
```

## Dockerfile Build

建置 backend image：

```powershell
docker build -t docurag-backend ./backend
```

建置包含 real OCR GPU dependency 的 backend image：

```powershell
docker build --build-arg DOCURAG_INSTALL_REAL_OCR=true -t docurag-backend-real-ocr ./backend
```

使用 Docker Compose 啟動 backend：

```powershell
docker compose -f infra/docker-compose.yml up -d --build
curl http://127.0.0.1:8000/health
docker compose -f infra/docker-compose.yml down
```

Compose real OCR runtime：

```powershell
$env:DOCURAG_INSTALL_REAL_OCR="true"
$env:DOCURAG_OCR_PROVIDER="paddleocr"
docker compose -f infra/docker-compose.yml up -d --build
curl http://127.0.0.1:8000/health
docker compose -f infra/docker-compose.yml down
```

## Repository Structure

```text
DocuRAG/
├── README.md
├── AGENTS.md
├── TODO.md
├── goal.md
├── .env.example
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   └── styles.css
│   ├── .env.example
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   └── README.md
├── infra/
│   └── docker-compose.yml
├── scripts/
│   ├── check-dev-env.ps1
│   ├── demo-smoke-test.ps1
│   ├── seed-demo-data.ps1
│   └── test-backend.ps1
├── sample-data/
│   ├── documents/
│   │   ├── README.md
│   │   ├── mock-contract-support.txt
│   │   ├── mock-invoice-aurora.txt
│   │   ├── sample-ocr-invoice.png
│   │   └── sample-ocr-zh-tw.png
│   └── eval/
│       └── README.md
├── docs/
│   ├── PRD.md
│   ├── ROADMAP.md
│   ├── LOCAL_DEV_SETUP.md
│   ├── api.md
│   ├── architecture.md
│   ├── db-schema.md
│   └── demo-script.md
└── tasks/
    ├── _TEMPLATE.md
    └── ...
```

Runtime data 會寫入 `data/`，包含 uploads 與 local metadata。這些內容是本機執行產物，不是主要文件結構的一部分。

## Documentation

- `goal.md`：完整產品構想與長期目標。
- `docs/PRD.md`：MVP 產品需求。
- `docs/architecture.md`：目前架構與延後項目。
- `docs/ROADMAP.md`：開發路線與 milestone。
- `docs/LOCAL_DEV_SETUP.md`：本機環境、Python 3.12、PaddleOCR 與 Docker 驗證補充。
- `docs/api.md`：API contract 補充。
- `backend/README.md`：backend 啟動、API、OCR provider 與 RAG 說明。
- `frontend/README.md`：frontend 啟動與 UI 行為說明。
- `tasks/`：ticket-first 開發任務票。

## Development Direction

本專案採用 ticket-first 工作流：

1. 每次只處理一張 `tasks/` 底下的小 ticket。
2. 實作前先讀 ticket 的 Goal、Scope、Out of Scope、Acceptance Criteria 與 Validation。
3. 每個 Phase 都要對應明確版本號；Phase 08 對應 `v0.8.0`、Phase 09 對應 `v0.9.0`、Phase 10 對應 `v0.10.0`。
4. 完成後更新對應 checklist、版本號與 release 文件，並執行 ticket 指定 validation。
5. 嚴格避免把後續 OCR、RAG、infra、auth 或 database scope 提前塞進當前 ticket。

## Release Status

- v0.0: repo structure、docs、tasks 已完成。
- v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- v0.2.0: Demo UI、backend CORS、Backend CI、Docker build / Compose 驗證已完成。
- v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI、Docker Compose upload 驗證已完成。
- v0.4.0: OCR Mock Pipeline、OCR result persistence、frontend OCR UI、Docker Compose OCR mock API 驗證已完成。
- v0.5.0: Local RAG Baseline、chunking、keyword retrieval、RAG answer API、frontend Chat UI 與 Docker Compose RAG API 驗證已完成。
- v0.5.1: Demo Hardening、公開 sample data、demo seed script、API smoke test、5 分鐘 demo flow 與 Docker Compose demo 驗證已完成。
- v0.6.0: Bridge Contracts、OCR provider interface、RAG provider interface、processing status、chunk citation schema 與 processing job contract 已完成。
- v0.7.0: Real OCR Provider Spike 已完成；選定 PaddleOCR、新增 provider-selected OCR endpoint、完成 output normalization 與 optional real OCR demo hardening。
- v0.8.0: PaddleOCR Runtime Stabilization 已完成；Python 3.12、PaddleOCR 2.10.0、PaddlePaddle 3.0.0 real OCR sample flow 已驗證，provider-selected OCR 預設走 PaddleOCR，mock flow 需透過 `/ocr/mock` 或 `DOCURAG_OCR_PROVIDER=mock` 明確 override。
- v0.9.0: GPU Runtime 已完成；real OCR runtime 收斂為 PaddlePaddle GPU-only，PaddleOCR 預設使用 PP-OCRv4 mobile 中文 / 中英混合模型設定，mock OCR path 不受影響。
