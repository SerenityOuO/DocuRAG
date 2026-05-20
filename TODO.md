# TODO

本 checklist 追蹤 DocuRAG AgentOps 目前的 Phase 00 到 Phase 02。每張 ticket 完成後應可單獨 commit，並更新對應項目。

## Phase 00 - Bootstrap Documents and Tickets

- [x] 建立 Phase 00 文件與任務票規範。
- [x] 更新 `README.md`，說明專案目標、MVP 範圍與開發方向。
- [x] 更新 `AGENTS.md`，說明 Codex 後續如何用小 ticket 開發。
- [x] 建立 `docs/PRD.md`。
- [x] 建立 `docs/ARCHITECTURE.md`。
- [x] 建立 `docs/ROADMAP.md`。
- [x] 建立 `tasks/_TEMPLATE.md`。
- [x] 建立 Phase 00 到 Phase 02 的初始 ticket。
- [ ] 執行 `tasks/phase-00-bootstrap/00-01-repo-structure.md`。
- [ ] 執行 `tasks/phase-00-bootstrap/00-02-project-docs.md`。

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
- [ ] 修復 Docker 後重跑 `docker build` 與 `docker compose build`。

## Parking Lot

- [ ] OCR / VLM parser。
- [ ] Qdrant indexing。
- [ ] Redis session / cache / rate limit。
- [ ] NATS worker。
- [ ] RAG chat / rerank / citation trace。
- [ ] vLLM / Ollama / OpenAI-compatible provider。

## Release Verification Status

- [x] v0.0: repo structure、docs、tasks 已完成。
- [x] v0.1.0: backend healthcheck、document upload stub、pytest、本機 `/health` HTTP 驗證已完成。
- [x] Python fallback: `scripts/check-dev-env.ps1` 與 `scripts/test-backend.ps1` 可透過 `pip.exe` 反推實際 `python.exe`。
- [x] Upload stub: pytest 與本機 HTTP 驗證皆通過。
- [ ] Docker: `docker` CLI 目前不在 PATH，Docker build / Compose 尚未驗證。
