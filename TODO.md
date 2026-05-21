# TODO

本 checklist 追蹤 DocuRAG AgentOps 目前的 Phase 00 到 v0.5.0。每張 ticket 完成後應可單獨 commit，並更新對應項目。

## Phase 00 - Bootstrap Documents and Tickets

- [x] 建立 Phase 00 文件與任務票規範。
- [x] 更新 `README.md`，說明專案目標、MVP 範圍與開發方向。
- [x] 更新 `AGENTS.md`，說明 Codex 後續如何用小 ticket 開發。
- [x] 建立 `docs/PRD.md`。
- [x] 建立 `docs/ARCHITECTURE.md`。
- [x] 建立 `docs/ROADMAP.md`。
- [x] 建立 `tasks/_TEMPLATE.md`。
- [x] 建立 Phase 00 到 Phase 02 的初始 ticket。
- [x] 執行 `tasks/phase-00-bootstrap/00-01-repo-structure.md`。
- [x] 執行 `tasks/phase-00-bootstrap/00-02-project-docs.md`。

## Phase 01 - Backend Bootstrap

- [x] 執行 `tasks/phase-01-backend-bootstrap/01-01-backend-healthcheck.md`。
- [x] 執行 `tasks/phase-01-backend-bootstrap/01-02-backend-docker.md`。
- [x] 確認 backend healthcheck 可以用 ticket 指定方式驗證。
- [x] 確認 Docker 啟動邊界只涵蓋 Phase 01 所需範圍。

## Phase 02 - Document Foundation

- [x] 執行 `tasks/phase-02-document-foundation/02-01-document-upload-api.md`。
- [x] 執行 `tasks/phase-02-document-foundation/02-02-document-metadata-schema.md`。
- [x] 確認文件上傳 API 不觸發 OCR、RAG 或 async worker。
- [x] 確認 document metadata schema 可支援後續 OCR 與 RAG 狀態，但不提前實作資料庫遷移。

## MVP v0.1 Local Verification

- [x] 建立 `scripts/check-dev-env.ps1`。
- [x] 建立 `scripts/test-backend.ps1`。
- [x] 建立 `docs/LOCAL_DEV_SETUP.md`。
- [x] 診斷 Python：`py` launcher 不存在，`python` 目前無法執行。
- [x] 診斷 Docker：`docker` CLI 不在 PATH。
- [x] 修復本機 Python 後重跑 `scripts/test-backend.ps1`。
- [x] 修復 Docker 後重跑 `docker build` 與 `docker compose build`。

## MVP v0.2 Demo UI

- [x] 建立 GitHub Actions `Backend CI` workflow。
- [x] 建立最小 Vue 3 + Vite + TypeScript frontend。
- [x] frontend 可呼叫 `GET /health`。
- [x] frontend 可選擇檔案並呼叫 `POST /documents/upload` stub。
- [x] backend 加上 local frontend CORS 設定。
- [x] 建立 `frontend/README.md`。
- [x] 更新 demo 啟動與驗證文件。
- [x] 驗證 Docker CLI、Docker build 與 Docker Compose healthcheck。

## MVP v0.3 Document Local Storage

- [x] 將 `POST /documents/upload` 從 stub 升級為本機存檔。
- [x] 保存 document metadata 到 local JSON store。
- [x] 新增 `GET /documents` 文件列表 API。
- [x] 新增 `GET /documents/{document_id}` 文件詳情 API。
- [x] 新增安全下載端點 `GET /documents/{document_id}/download`。
- [x] 測試 unsafe filename 不會 path traversal。
- [x] frontend 顯示文件列表與 document metadata JSON。
- [x] Docker Compose 掛載 `data/` 並驗證 upload API。

## MVP v0.4 OCR Mock Pipeline

- [x] 建立 `tasks/phase-03-ocr-mock/03-01-ocr-mock-pipeline.md`。
- [x] 新增 `POST /documents/{document_id}/ocr/mock`。
- [x] 新增 `GET /documents/{document_id}/ocr`。
- [x] 保存 OCR mock result 到 local JSON metadata store。
- [x] 未執行 OCR 的文件回傳 `pending` OCR status。
- [x] OCR result 包含 status、text、extracted fields 與 updated timestamp。
- [x] frontend 可對文件執行 Run Mock OCR。
- [x] frontend 顯示 OCR status、OCR text 與 extracted fields。
- [x] 確認未接 PaddleOCR、Tesseract、VLM、RAG、Qdrant、Redis、NATS、vLLM、登入或 PostgreSQL。

## MVP v0.5 Local RAG Baseline

- [x] 建立 `tasks/phase-05-rag-baseline/05-01-local-rag-baseline.md`。
- [x] 從 OCR mock text 產生 chunks。
- [x] 每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source` 與 `created_at`。
- [x] chunks 保存到 local JSON metadata store，不新增 DB。
- [x] 新增 local keyword retrieval，依 query 回傳 `top_k` matched chunks。
- [x] retrieval result 包含 score、`document_id` 與 `chunk_id`。
- [x] 新增 `POST /rag/query`。
- [x] RAG response 包含 deterministic answer、citations 與 retrieved chunks。
- [x] citations 包含 `document_id`、`filename` 與 `chunk_id`。
- [x] frontend 新增 RAG chat，可顯示 answer、citations 與 retrieved chunks。
- [x] 保留既有 health、upload、document list 與 OCR mock UI。
- [x] backend version 更新為 `0.5.0`。
- [x] frontend package version 更新為 `0.5.0`。
- [x] 確認未接真正 LLM、OpenAI API、Ollama、vLLM、embedding、Qdrant、rerank、Redis、NATS、PostgreSQL、登入或 RBAC。

## Parking Lot

- [ ] 真正 OCR / VLM parser。
- [ ] Embedding 與 Qdrant indexing。
- [ ] Redis session / cache / rate limit。
- [ ] NATS worker。
- [ ] LLM-based RAG generation / rerank / citation trace evaluation。
- [ ] vLLM / Ollama / OpenAI-compatible provider。

## Release Verification Status

- [x] v0.0: repo structure、docs、tasks 已完成。
- [x] v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- [x] Python fallback: `scripts/check-dev-env.ps1` 與 `scripts/test-backend.ps1` 可透過 `pip.exe` 反推實際 `python.exe`。
- [x] Upload stub: pytest 與本機 HTTP 驗證皆通過。
- [x] Docker: `docker` CLI、Docker build 與 Docker Compose healthcheck 已驗證。
- [x] v0.2.0: Demo UI、backend CORS、Backend CI 與 Docker 驗證已完成。
- [x] v0.3.0: Document Local Storage、文件列表、文件詳情、frontend list UI 與 Docker Compose upload 驗證已完成。
- [x] v0.4.0: OCR Mock Pipeline、frontend OCR UI 與 Docker Compose OCR mock API 驗證已完成。
- [x] v0.5.0: Local RAG Baseline、frontend Chat UI 與 Docker Compose RAG API 驗證已完成。
