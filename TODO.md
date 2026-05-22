# TODO

本 checklist 追蹤 DocuRAG AgentOps 目前的 Phase 00 到 v0.7 ticket backlog。每張 ticket 完成後應可單獨 commit，並更新對應項目。

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

## MVP v0.5.1 Demo Hardening

- [x] 建立 `tasks/phase-05-rag-baseline/05-02-demo-hardening.md`。
- [x] 建立公開 sample documents，不包含真實個資或公司敏感資料。
- [x] 建立 `scripts/seed-demo-data.ps1`，可自動 upload、OCR mock、RAG query。
- [x] seed script 輸出 answer、citations 與 retrieved chunks。
- [x] 建立 `scripts/demo-smoke-test.ps1`，可驗證 `/health`、upload、OCR mock 與 `/rag/query`。
- [x] README 加入 5 分鐘 demo 指令、backend/frontend/Docker 啟動方式、範例問題與預期結果。
- [x] backend README 與 frontend README 加入 v0.5.1 demo flow。
- [x] OCR mock 對 text sample 納入公開 sample 文字，方便 local keyword RAG demo。
- [x] backend version 更新為 `0.5.1`。
- [x] frontend package version 更新為 `0.5.1`。
- [x] 確認仍未接 Qdrant、embedding、rerank、真正 LLM、OpenAI API、Ollama、vLLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## MVP v0.6 Bridge Contracts

- [x] 建立 `tasks/phase-06-bridge/06-01-ocr-provider-interface.md`。
- [x] 建立 `tasks/phase-06-bridge/06-02-rag-provider-interface.md`。
- [x] 建立 `tasks/phase-06-bridge/06-03-processing-status-contract.md`。
- [x] 建立 `tasks/phase-06-bridge/06-04-chunk-citation-schema.md`。
- [x] 建立 `tasks/phase-06-bridge/06-05-processing-job-contract.md`。
- [x] 執行 OCR provider interface bridge，保留 mock provider 並維持 OCR API 相容。
- [x] 執行 RAG provider interface bridge，保留 local keyword provider 並維持 `/rag/query` 相容。
- [x] 執行 processing status contract，明確定義 upload、OCR、indexing、ready 與 failed 狀態。
- [x] 執行 chunk / citation schema bridge，補齊 page、bbox、confidence 與 trace metadata contract。
- [x] 執行 processing job contract，建立同步 job metadata，不引入真正 worker 或 queue。
- [x] 確認 v0.6 bridge 階段仍未接真正 OCR、embedding、Qdrant、rerank、LLM、Redis、NATS、PostgreSQL、登入或 RBAC。

## MVP v0.7 Real OCR Provider Spike

- [x] 建立 `tasks/phase-07-real-ocr-provider/07-01-ocr-provider-decision.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-02-ocr-provider-adapter.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-03-ocr-output-normalization.md`。
- [x] 建立 `tasks/phase-07-real-ocr-provider/07-04-real-ocr-demo-hardening.md`。
- [x] 執行 OCR provider decision spike，選定 PaddleOCR，並定義 real provider 不可用時明確失敗、mock path 保持可用。
- [x] 執行 local OCR provider adapter，新增 provider-selected `/documents/{document_id}/ocr`，預設仍保留 mock provider。
- [x] 執行 OCR output normalization，將 PaddleOCR lines 映射到 page、bbox、confidence 與 trace metadata。
- [x] 執行 real OCR demo hardening，讓缺少 real OCR dependency 時 mock demo 仍可重跑。
- [x] frontend UI 只顯示目前版本號，並提供 provider-selected OCR 操作。
- [x] backend 與 frontend 版本更新為 `0.7.0`。
- [x] 確認 Phase 07 仍未接 queue、Redis、NATS、Qdrant、embedding、rerank、LLM、PostgreSQL、登入或 RBAC。

## Phase 08 - PaddleOCR Runtime Stabilization

- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-01-paddleocr-environment-baseline.md`。
- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-02-paddleocr-dependency-fix.md`。
- [x] 執行 `tasks/phase-08-paddleocr-runtime/08-03-paddleocr-default-flow-validation.md`。
- [x] 確認預設 PaddleOCR flow 可驗證，且 mock override 仍可重跑。
- [x] 確認 Phase 08 不新增 PDF rendering、Qdrant、embedding、rerank、LLM、Redis、NATS、worker、資料庫 schema、登入或權限。

- [x] 以 Python 3.12、PaddleOCR 2.10.0 與 PaddlePaddle 3.0.0 驗證 real OCR sample，可完成 provider-selected OCR 與 chunks 產生。
## Parking Lot

- [ ] Production-grade OCR / VLM parser（v0.7 只先做單一 provider spike）。
- [ ] Embedding 與 Qdrant indexing。
- [ ] Redis session / cache / rate limit。
- [ ] NATS worker。
- [ ] LLM-based RAG generation / rerank / citation trace evaluation。
- [ ] vLLM / Ollama / OpenAI-compatible provider。

## Phase 09 - GPU Runtime Backlog

- [ ] `tasks/phase-09-gpu-runtime/09-01-paddleocr-gpu-only-runtime.md`: PaddleOCR GPU-only runtime baseline。
- [ ] `tasks/phase-09-gpu-runtime/09-02-paddleocr-v4-mobile-chinese-model.md`: PaddleOCR PP-OCRv4 mobile 中文 / 中英混合模型。

## Phase 10 - LLM RAG Backlog

- [ ] `tasks/phase-10-llm-rag/10-01-llm-provider-decision.md`: 選定第一個本機大模型 provider。
- [ ] `tasks/phase-10-llm-rag/10-02-openai-compatible-llm-client.md`: 新增 OpenAI-compatible LLM client。
- [ ] `tasks/phase-10-llm-rag/10-03-llm-rag-generation.md`: 在既有 citations contract 上加入 LLM answer generation。
- [ ] `tasks/phase-10-llm-rag/10-04-llm-demo-smoke.md`: 補齊 LLM demo smoke 與 UI answer source。

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
- [x] v0.5.1: Demo Hardening、公開 sample data、demo seed script、API smoke test 與 Docker Compose demo 驗證已完成。
- [x] v0.6.0: Bridge Contracts、OCR provider interface、RAG provider interface、processing status、chunk citation schema 與 processing job contract。
- [x] v0.7.0: Real OCR Provider Spike 已完成；07-01 到 07-04 已執行，Docker validation 需待 Docker Desktop daemon 可用後重跑。
