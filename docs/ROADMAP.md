# Roadmap

本 roadmap 只列出 Phase 00、Phase 01 與 Phase 02，對應目前任務票。後續 OCR、RAG、AgentOps 與 infra 延伸會在完成這三個 phase 後再拆票。

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
- TODO 包含 Phase 00 到 Phase 02 checklist。

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

Next Candidate Milestone：

- v0.4.0 OCR mock pipeline：只建立可替換的 mock OCR 結果與狀態顯示，不接真正 OCR engine。
- v0.4.0 RAG baseline spike：只做 fixture-based retrieval baseline，不接 Qdrant 或 embeddings service。

## Release Verification

- v0.0: repo structure、docs、tasks 已完成。
- v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- v0.2.0: Demo UI、Backend CI、backend CORS、Docker build / Compose healthcheck 已完成。
- v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI、Docker build / Compose healthcheck / Compose upload API 已完成。
