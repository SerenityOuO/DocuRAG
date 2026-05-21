# Roadmap

本 roadmap 記錄 Phase 00 到 v0.5.1 的已交付切片，並新增 v0.6 bridge contracts 作為接真正 OCR、embedding、Qdrant、LLM RAG、AgentOps 與 infra 前的銜接層。

## Phase 00 - Bootstrap Documents and Tickets

Goal：建立可協作、可逐步開發的 repo 文件與 ticket 系統。

Deliverables：

- `README.md`
- `AGENTS.md`
- `TODO.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `tasks/_TEMPLATE.md`
- `tasks/phase-00-bootstrap/00-01-repo-structure.md`
- `tasks/phase-00-bootstrap/00-02-project-docs.md`

Acceptance：

- 所有 Phase 00 文件存在。
- README 說明專案目標、MVP 範圍與開發方向。
- AGENTS 說明小 ticket 開發流程。
- TODO 包含 Phase 00 到 v0.5.1 checklist。

## Phase 01 - Backend Bootstrap

Goal：建立 backend 最小可驗證入口，不實作業務功能。

Tickets：

- `tasks/phase-01-backend-bootstrap/01-01-backend-healthcheck.md`
- `tasks/phase-01-backend-bootstrap/01-02-backend-docker.md`

Expected Outcome：

- backend 有最小 `/health`。
- healthcheck 可以用測試或手動 request 驗證。
- Docker 邊界只包住 Phase 01 所需的 backend 啟動，不加入 Redis、NATS、Qdrant 或 vLLM。

## Phase 02 - Document Foundation

Goal：建立文件領域的最小 API 與 metadata contract。

Tickets：

- `tasks/phase-02-document-foundation/02-01-document-upload-api.md`
- `tasks/phase-02-document-foundation/02-02-document-metadata-schema.md`

Expected Outcome：

- 可以定義文件上傳 API 的 request / response 行為。
- 可以描述 document metadata 與狀態流轉。
- 不觸發 OCR、RAG、worker、Qdrant 或 Redis。

## Roadmap Guardrails

- Phase 00 只做文件與票券。
- Phase 01 只做 backend 啟動與 healthcheck。
- Phase 02 只做文件上傳與 metadata foundation。
- v0.4.0 只做 OCR mock pipeline，不接真正 OCR engine 或 async worker。
- v0.5.0 只做 local RAG baseline，不接 LLM、OpenAI API、Ollama、vLLM、embedding、Qdrant 或 rerank。
- v0.5.1 只做 demo hardening，不新增 Qdrant、embedding、rerank、真正 LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。
- v0.6.0 只做 bridge contracts，不接真正 OCR、embedding、Qdrant、rerank、LLM、Redis、NATS、PostgreSQL、登入或 RBAC。
- 每張 ticket 完成後才進下一張，不平行擴張範圍。

## v0.2.0 Demo UI Milestone

Goal：建立可面試展示的最小 UI，讓使用者能看到 backend health，並把檔案送到既有 `/documents/upload` stub。

Expected Outcome：

- GitHub Actions `Backend CI` 會在 push 與 pull request 執行 backend pytest。
- Vue 3 + Vite frontend 使用 `VITE_API_BASE_URL` 呼叫 backend。
- backend CORS 允許 `http://localhost:5173` 與 `http://127.0.0.1:5173`。
- Docker CLI、backend Docker build、Compose build、Compose up healthcheck 可驗證。
- 不新增 OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限或資料庫 schema。

## v0.3.0 Document Local Storage Milestone

Goal：把文件上傳從 stub 升級為可驗證的本機 storage MVP，讓 demo 可以呈現「上傳後真的保存、可列出、可查詳情」。

Expected Outcome：

- `POST /documents/upload` 會將原始檔保存到 `data/uploads/`。
- document metadata 會保存到 `data/documents.json`。
- `GET /documents` 依 `created_at` 由新到舊回傳文件列表。
- `GET /documents/{document_id}` 回傳指定文件 metadata，找不到時回傳 404。
- frontend 在上傳成功後刷新文件列表，並可點選文件查看 metadata JSON。
- Docker Compose 掛載 repo root 的 `data/` 到 container `/app/data`，啟動後可通過 healthcheck 與 upload API 驗證。
- 不新增 OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限、PostgreSQL、embedding、rerank 或 Agent。

## v0.4.0 OCR Mock Pipeline Milestone

Goal：建立可替換的 OCR mock pipeline，讓 demo 可以呈現「文件上傳後可執行 OCR、保存結果、前端顯示文字與欄位」。

Ticket：

- `tasks/phase-03-ocr-mock/03-01-ocr-mock-pipeline.md`

Expected Outcome：

- `POST /documents/{document_id}/ocr/mock` 對既有文件產生 deterministic mock OCR text 與 extracted fields。
- `GET /documents/{document_id}/ocr` 回傳 OCR status、text、extracted fields 與 updated timestamp。
- 未執行 OCR 的文件回傳 `pending` OCR status。
- OCR result 保存到 `data/documents.json` 的對應 document metadata。
- frontend 可在文件詳情執行 Run Mock OCR。
- frontend 顯示 OCR status、OCR text 與 extracted fields。
- 不新增 PaddleOCR、Tesseract、VLM、RAG、Qdrant、Redis、NATS、vLLM、登入、RBAC 或 PostgreSQL。

## v0.5.0 Local RAG Baseline Milestone

Goal：使用 v0.4.0 的 OCR mock text 作為知識來源，建立第一版可驗證的 local RAG baseline。

Ticket：

- `tasks/phase-05-rag-baseline/05-01-local-rag-baseline.md`

Expected Outcome：

- OCR mock 完成後會從 OCR text 產生 chunks，並保存到 local JSON metadata store。
- 每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。
- `POST /rag/query` 接收 `query` 與 `top_k`。
- local keyword retrieval 從 chunks 回傳 matched chunks、score、`document_id` 與 `chunk_id`。
- RAG response 包含 deterministic answer、citations 與 retrieved chunks。
- citations 指出 `document_id`、`filename` 與 `chunk_id`。
- frontend 新增 RAG chat，顯示 answer、citations 與 retrieved chunks。
- 不新增真正 LLM、OpenAI API、Ollama、vLLM、embedding、Qdrant、rerank、Redis、NATS、PostgreSQL、登入或 RBAC。

## v0.5.1 Demo Hardening Milestone

Goal：讓 v0.5.0 的 upload -> OCR mock -> local RAG -> citations 流程更適合 GitHub 與面試展示。

Ticket：

- `tasks/phase-05-rag-baseline/05-02-demo-hardening.md`

Expected Outcome：

- `sample-data/documents/` 提供公開虛構 sample documents，不包含真實個資或公司敏感資料。
- `scripts/seed-demo-data.ps1` 可自動上傳 sample、執行 OCR mock、執行 local RAG query，並輸出 answer、citations、retrieved chunks。
- `scripts/demo-smoke-test.ps1` 可重跑驗證 `/health`、upload、OCR mock 與 `/rag/query`。
- README 提供 5 分鐘 demo 指令、backend/frontend/Docker 啟動方式、範例問題與預期結果。
- `/health` 回傳 version `0.5.1`。
- demo 明確標示目前是 local keyword RAG baseline，不是 embedding、Qdrant、rerank 或 LLM。
- 不新增 Qdrant、embedding、rerank、真正 LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## v0.6.0 Bridge Contracts Milestone

Goal：在真正 OCR / RAG provider 進場前，先把可替換邊界、處理狀態、chunk / citation metadata 與 processing job contract 打穩，避免後續接模型時重寫既有 API 與 frontend demo flow。

Tickets：

- `tasks/phase-06-bridge/06-01-ocr-provider-interface.md`
- `tasks/phase-06-bridge/06-02-rag-provider-interface.md`
- `tasks/phase-06-bridge/06-03-processing-status-contract.md`
- `tasks/phase-06-bridge/06-04-chunk-citation-schema.md`
- `tasks/phase-06-bridge/06-05-processing-job-contract.md`

Expected Outcome：

- OCR mock 會被整理成最小 OCR provider / service 邊界，仍只保留 mock provider。
- local keyword RAG 會被整理成最小 RAG provider / service 邊界，仍只保留 keyword provider。
- document processing status 可清楚描述 upload、OCR、indexing、ready 與 failed 流轉。
- chunk 與 citation schema 可承接 page、bbox、confidence 與 trace metadata，但不實作真正 OCR bbox 或 citation evaluation。
- processing job contract 可記錄本機同步 job metadata，但不引入真正 worker、queue、Redis 或 NATS。
- 既有 upload -> OCR mock -> local RAG -> citations demo flow 保持可用。
- 不新增真正 OCR engine、embedding、Qdrant、rerank、LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。

Next Candidate Milestone：

- v0.7.0 Real OCR Provider Spike：在 v0.6 bridge contracts 完成後，挑一個本機 OCR / VLM provider 做可驗證 spike。
- v0.8.0 Embedding / Qdrant Indexing Spike：在 OCR 與 chunk / citation contract 穩定後，將 local keyword retrieval 替換成可驗證的 vector indexing。

## Release Verification

- v0.0: repo structure、docs、tasks 已完成。
- v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- v0.2.0: Demo UI、Backend CI、backend CORS、Docker build / Compose healthcheck 已完成。
- v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI、Docker build / Compose healthcheck / Compose upload API 已完成。
- v0.4.0: OCR Mock Pipeline、OCR result persistence、frontend OCR UI、Docker build / Compose healthcheck / Compose upload / Compose OCR mock API 已完成。
- v0.5.0: Local RAG Baseline、chunking、keyword retrieval、RAG answer API、frontend Chat UI、Docker build / Compose healthcheck / Compose upload / Compose OCR mock / Compose RAG API 已完成。
- v0.5.1: Demo Hardening、公開 sample data、demo seed script、API smoke test、5 分鐘 README demo flow、Docker build / Compose demo smoke / seed script 已完成。
- v0.6.0: Bridge Contracts、OCR provider interface、RAG provider interface、processing status、chunk citation schema 與 processing job contract 待執行。
