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

MVP 初期可以使用 fixture 或最小資料結構，不要求真正 AI pipeline。以下能力保留為後續階段：

- 真正 OCR / VLM parser。
- 真正 embeddings / Qdrant indexing。
- 真正 Redis session / NATS worker。
- 真正 rerank / RAG generation。
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

目前 Phase 00 文件與任務票使用以下結構：

```text
DocuRAG/
├── README.md
├── AGENTS.md
├── TODO.md
├── goal.md
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── ROADMAP.md
└── tasks/
    ├── _TEMPLATE.md
    ├── phase-00-bootstrap/
    ├── phase-01-backend-bootstrap/
    └── phase-02-document-foundation/
```

後續 ticket 才會建立 backend、frontend、infra 或 package manager 檔案。

## Documentation

- `goal.md`：完整產品構想與長期目標。
- `docs/PRD.md`：依 `goal.md` 收斂後的 MVP 產品需求。
- `docs/ARCHITECTURE.md`：MVP 架構與明確延後的元件。
- `docs/ROADMAP.md`：Phase 00 到 Phase 02 的開發路線。
- `TODO.md`：目前階段 checklist。
- `tasks/`：可單次完成、可單獨 commit 的任務票。

## Current Status

目前停在 Phase 00 文件與任務票建立階段，尚未實作 backend、frontend、OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限或資料庫 schema。
