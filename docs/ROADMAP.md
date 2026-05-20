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
