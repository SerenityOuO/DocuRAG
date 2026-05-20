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

- [ ] 執行 `tasks/phase-01-backend-bootstrap/01-01-backend-healthcheck.md`。
- [ ] 執行 `tasks/phase-01-backend-bootstrap/01-02-backend-docker.md`。
- [ ] 確認 backend healthcheck 可以用 ticket 指定方式驗證。
- [ ] 確認 Docker 啟動邊界只涵蓋 Phase 01 所需範圍。

## Phase 02 - Document Foundation

- [ ] 執行 `tasks/phase-02-document-foundation/02-01-document-upload-api.md`。
- [ ] 執行 `tasks/phase-02-document-foundation/02-02-document-metadata-schema.md`。
- [ ] 確認文件上傳 API 不觸發 OCR、RAG 或 async worker。
- [ ] 確認 document metadata schema 可支援後續 OCR 與 RAG 狀態，但不提前實作資料庫遷移。

## Parking Lot

- [ ] OCR / VLM parser。
- [ ] Qdrant indexing。
- [ ] Redis session / cache / rate limit。
- [ ] NATS worker。
- [ ] RAG chat / rerank / citation trace。
- [ ] vLLM / Ollama / OpenAI-compatible provider。
