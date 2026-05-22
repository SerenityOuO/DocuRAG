# DocuRAG AgentOps

DocuRAG AgentOps 是一個面試展示用的 AI 文件平台 side project，用來呈現企業級文件上傳、OCR、local RAG、citation trace 與 AgentOps 產品思維。

目前主線已完成 local document workflow、provider-selected PaddleOCR OCR flow、PP-OCRv4 mobile 中文 / 中英混合模型設定、backend startup preload、provider reuse、OCR timing metadata、mock OCR override、local keyword RAG baseline、可選 Ollama Qwen3.5 RAG generation demo、可選 manual vector indexing + Qdrant vector retrieval demo、retrieval evaluation baseline、disabled-by-default vector rerank eval spike、optional hybrid retrieval eval strategy、frontend demo UI，以及可重跑的本機 backend validation。這仍是受控 MVP，不是 production OCR / RAG 平台。

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
- Backend startup 會在 selected provider 為 PaddleOCR 時 preload engine；provider-selected OCR request 會重用同一個 provider / engine。
- PaddleOCR result metadata 會輸出 safe timing 欄位：engine preload / request load / inference / normalization / total duration。
- v0.9.1 預設 `DOCURAG_OCR_USE_ANGLE_CLS=false`、`DOCURAG_OCR_DET_LIMIT_SIDE_LEN=960`、`DOCURAG_OCR_REC_BATCH_NUM=6`；mock OCR path 不受影響。
- Local keyword RAG baseline，回傳 deterministic answer、citations 與 retrieved chunks。
- v0.10.0 已固定 LLM / VLM 第一版目標為 Ollama `qwen3.5:4b`，並新增最小 Ollama LLM client、可選 `/rag/query` generation path、demo smoke `-RunLlm` 與 frontend answer source；未啟用 LLM provider 時預設仍是 deterministic keyword baseline。
- v0.11.0 已新增 disabled-by-default Ollama embedding client、optional Qdrant local runtime / collection smoke 與 fallback-safe vector retrieval path。
- v0.12.0 已新增 manual vector indexing service / API；只有明確呼叫 `POST /documents/{document_id}/index/vector` 後，vector retrieval demo 才會查詢已索引到 Qdrant 的 chunks，失敗會回到 keyword baseline。
- v0.13.0 已新增公開 retrieval eval dataset、本機 evaluation runner、Hit Rate@K / MRR@K / Recall@K / latency / failure count metrics，以及 baseline / optional vector eval smoke。
- v0.15.0 已新增 disabled-by-default FastEmbed rerank adapter building block、optional `vector_rerank` eval strategy、rerank trace metadata 與 `-RunVectorRerank` smoke flag；未啟用 rerank provider 時會保留 vector candidates 並記錄 fallback reason。
- v0.16.0 已將公開 retrieval eval dataset 擴充到 12 筆，新增 optional `hybrid` eval strategy 與 `-RunHybrid` smoke flag；`hybrid` 只用於 eval runner，不接 `/rag/query` 或 frontend UI。
- v0.17.0 已新增 frontend compact retrieval trace panel，並改善 retrieval eval summary visibility；UI 只讀既有 RAG response metadata，eval summary 顯示 fallback count、trace metadata count 與 result strategy counts，不新增 backend API 或 production eval dashboard。
- v0.18.0 已完成 `hybrid_rerank` planning backlog；這是 Markdown-only planning，不代表 runtime、eval runner、frontend UI 或 smoke flag 已可用。
- Vue 3 + Vite frontend，可操作 upload、document list/detail、selected OCR、mock override、OCR result 與 RAG chat。
- Python 3.12 backend runtime；real OCR 只支援 PaddlePaddle GPU / CUDA runtime，dependency 收斂在 `backend[real-ocr]` optional extra。
- Dockerfile / Docker Compose backend runtime，real OCR GPU dependency 可透過 build arg 開啟。

目前仍刻意不實作：

- PDF rendering、image preprocessing、版面分析、多頁文件處理或 OCR accuracy tuning。
- Default-on vector retrieval、default-on rerank、default-on hybrid retrieval、`hybrid_rerank`、LLM-as-judge、answer faithfulness scoring、eval dashboard、LLM generation default-on path、streaming UI、OpenAI API 或 vLLM serving。
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

可選 Ollama RAG generation demo 需要先啟動 Ollama 並確認 `qwen3.5:4b` 在本機模型清單中，再用 LLM env 啟動 backend：

```powershell
$env:DOCURAG_LLM_PROVIDER="ollama"
$env:DOCURAG_LLM_BASE_URL="http://127.0.0.1:11434"
$env:DOCURAG_LLM_MODEL="qwen3.5:4b"
py -3.12 -m uvicorn app.main:app --reload
```

回到 repo root 後可執行 baseline smoke 與 LLM smoke：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunLlm
```

可選 Ollama embedding / Qdrant collection smoke：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ollama-embedding-smoke.ps1
docker-compose -f infra/docker-compose.yml up -d qdrant
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\qdrant-collection-smoke.ps1
docker-compose -f infra/docker-compose.yml down
```

`qwen3-embedding:0.6b` 需先透過 Ollama pull；`docurag_chunks_v1` 預設 vector size 為 `1024`，對應 `Qwen3-Embedding-0.6B` model card 的 embedding dimension。未設定 vector retrieval env 時 `/rag/query` 仍走 keyword baseline。

可選 Vector RAG demo 需要同時啟動 Ollama embedding model 與 Qdrant，再用 vector env 啟動 backend；`-RunVector` smoke 會在 OCR mock 後先呼叫 manual indexing API，再執行 vector retrieval query：

```powershell
$env:DOCURAG_RAG_RETRIEVAL_PROVIDER="vector"
$env:DOCURAG_EMBEDDING_PROVIDER="ollama"
$env:DOCURAG_EMBEDDING_MODEL="qwen3-embedding:0.6b"
$env:DOCURAG_QDRANT_URL="http://127.0.0.1:6333"
$env:DOCURAG_QDRANT_COLLECTION="docurag_chunks_v1"
py -3.12 -m uvicorn app.main:app --reload
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunVector
```

Retrieval evaluation baseline 可在沒有 Ollama embedding 或 Qdrant 時直接跑 keyword metrics；輸出 JSON 預設寫到 `.tmp/retrieval-eval-result-keyword.json`：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1
```

Optional vector eval 需要先啟動 Ollama embedding model、Qdrant collection，並用上方 vector env 啟動 backend。`-RunVector` 會先透過 manual vector indexing API 做 preflight，再輸出 vector metrics 到 `.tmp/retrieval-eval-result-vector.json`：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVector
```

Optional `vector_rerank` eval 需要同樣的 Ollama embedding、Qdrant collection 與 vector-enabled backend，並可設定 disabled-by-default rerank env。若 FastEmbed rerank runtime 尚未安裝，eval 會保留 vector candidates 並在 chunk metadata 記錄 rerank fallback；若 runtime 可用，會輸出 rerank scores 與 trace metadata 到 `.tmp/retrieval-eval-result-vector-rerank.json`：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVectorRerank
```

Optional `hybrid` eval 需要同樣的 Ollama embedding、Qdrant collection 與 vector-enabled backend。`hybrid` 只接入 retrieval eval runner，會 merge / dedupe keyword 與 vector candidates，輸出 hybrid trace metadata 到 `.tmp/retrieval-eval-result-hybrid.json`；這不代表 `/rag/query` 或 frontend UI 已支援 hybrid。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybrid
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

若本機只有 standalone `docker-compose` CLI，可把上方 `docker compose` 改成 `docker-compose`。Compose 內也包含 optional Qdrant service；backend 沒有 `depends_on` Qdrant，因此 Qdrant 不可用不會阻塞既有 backend demo。

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
│   ├── retrieval-eval-smoke.ps1
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
│       ├── README.md
│       └── retrieval-eval.json
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
3. 每個 Phase 都要對應明確版本號；Phase 08 對應 `v0.8.0`、Phase 09 對應 `v0.9.0`、Phase 09 performance hardening 對應 `v0.9.1`、Phase 10 對應 `v0.10.0`、Phase 11 對應 `v0.11.0`、Phase 12 對應 `v0.12.0`、Phase 13 對應 `v0.13.0`、Phase 15 對應 `v0.15.0`、Phase 16 對應 `v0.16.0`、Phase 17 對應 `v0.17.0`、Phase 18 對應 `v0.18.0`、Phase 19 對應 `v0.19.0`。
4. 完成後更新對應 checklist、版本號與 release 文件，並執行 ticket 指定 validation。
5. 嚴格避免把後續 OCR、RAG、infra、auth 或 database scope 提前塞進當前 ticket。

Phase 09 performance hardening 已在 `v0.9.1` 完成。Phase 10 已在 `v0.10.0` 完成 provider decision、Ollama Qwen3 client、optional RAG generation path、demo smoke 與 answer source UI。Phase 11 已在 `v0.11.0` 完成 optional Vector RAG demo。Phase 12 已在 `v0.12.0` 完成 Vector Indexing Hardening，只做 manual vector indexing contract / service / API / demo smoke，沒有擴張到 rerank、hybrid search、eval runner、worker、DB、登入或 RBAC。Phase 13 已在 `v0.13.0` 完成 Retrieval Evaluation Baseline，建立公開 eval dataset、Hit Rate / MRR / Recall metrics runner、baseline eval smoke 與 optional vector eval smoke。Phase 15 已在 `v0.15.0` 完成 disabled-by-default `vector_rerank` runtime spike。Phase 16 已在 `v0.16.0` 完成 dataset expansion 與 optional `hybrid` eval strategy。Phase 17 已在 `v0.17.0` 完成 retrieval trace UI / eval visibility。Phase 18 已完成 `hybrid_rerank` planning-only backlog，不 bump version、不新增 runtime。Phase 19 已新增為 interview MVP packaging backlog，優先處理 demo 文件刷新、sample / eval coverage、截圖或 GIF 與 final validation；`hybrid_rerank` runtime、production eval dashboard、worker、DB、auth 與 deployment 仍留給後續 Phase。

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
- v0.9.1: OCR Performance Hardening 已完成；backend startup preload、provider / engine reuse、OCR timing log / metadata、`cls=False` baseline 與 v0.9.1 文件版本同步已完成。
- v0.10.0: LLM RAG Backlog 已完成；Ollama `qwen3.5:4b` provider decision、最小 client、optional `/rag/query` generation path、demo smoke `-RunLlm`、frontend answer source 與版本文件同步已完成。
- v0.11.0: Vector RAG Backlog 已完成；Ollama `qwen3-embedding:0.6b` embedding client、Qdrant local runtime / collection smoke、optional vector retrieval path、fallback trace metadata、demo smoke `-RunVector` 與版本文件同步已完成。
- v0.12.0: Vector Indexing Hardening 已完成；manual vector indexing contract、同步 indexing service、`POST /documents/{document_id}/index/vector`、optional vector indexing smoke 與版本文件同步已完成。
- v0.13.0: Retrieval Evaluation Baseline 已完成；公開 eval dataset、retrieval eval runner、Hit Rate@K / MRR@K / Recall@K / latency / failure count metrics、baseline eval smoke、optional vector eval smoke 與版本文件同步已完成。
- v0.15.0: Rerank Runtime Spike 已完成；FastEmbed rerank provider decision、disabled-by-default rerank adapter、optional `vector_rerank` eval strategy、rerank trace metadata、baseline smoke 與版本文件同步已完成。
- v0.16.0: Hybrid Retrieval Slice 已完成；公開 eval dataset 擴充到 12 筆、optional `hybrid` eval strategy、hybrid trace metadata、baseline smoke、optional `-RunHybrid` smoke 與版本文件同步已完成。
- v0.17.0: Retrieval Trace UI / Eval Visibility 已完成；frontend retrieval trace panel、eval summary fallback / trace metadata reporting、baseline demo smoke、baseline eval smoke 與版本文件同步已完成。
