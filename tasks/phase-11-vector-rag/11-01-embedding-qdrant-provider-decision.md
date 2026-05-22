# 11-01 Embedding And Qdrant Provider Decision

## Goal

固定 Phase 11 vector RAG 的第一版 provider decision，明確定義 embedding model、vector store、資料 contract 與後續 ticket 切分，避免在第一張票就直接引入 Qdrant runtime 或大範圍 RAG rewrite。

## Scope

- 選定 Phase 11 第一版 embedding provider 與 model。
- 選定 Phase 11 第一版 vector store provider。
- 記錄 local-only demo 目標、資料 contract、metadata filtering 需求與 fallback 行為。
- 更新 `TODO.md` 與 `docs/ROADMAP.md`，新增 Phase 11 / `v0.11.0` backlog。
- 保留既有 keyword RAG 與 optional Ollama generation path。

Provider decision：

- Embedding provider：Ollama native embedding API。
- Embedding endpoint：`DOCURAG_EMBEDDING_BASE_URL=http://127.0.0.1:11434`。
- Embedding model：`DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b`。
- 選擇理由：Ollama 官方 library 提供 `qwen3-embedding`，支援 `/api/embed`，其中 `0.6b` tag 約 639MB，適合作為本機 demo 起步；Qwen3 Embedding 系列定位為 text embedding，且具 multilingual 能力，適合中英混合 OCR chunks。
- Vector store：Qdrant self-hosted Docker / Docker Compose，後續可用 REST API 或 Python client 接入。
- Qdrant local endpoint：`DOCURAG_QDRANT_URL=http://127.0.0.1:6333`。
- Collection name：`docurag_chunks_v1`。
- Initial vector dimension：以實際 `qwen3-embedding:0.6b` `/api/embed` 回傳長度為準；11-02 必須用 smoke test 固定並寫入文件，不在本票硬編碼。
- Payload metadata：至少包含 `document_id`、`filename`、`chunk_id`、`source_type`、`page_number`、`ocr_provider`、`created_at`，後續 project / organization 欄位等 auth scope 排定後再納入。

References：

- Ollama `qwen3-embedding` library：`https://ollama.com/library/qwen3-embedding`
- Ollama embeddings docs：`https://docs.ollama.com/capabilities/embeddings`
- Qdrant local quickstart：`https://qdrant.tech/documentation/quick-start/`
- Qdrant Python client quickstart：`https://python-client.qdrant.tech/quickstart`

## Out of Scope

- 不實作 embedding client。
- 不下載或 pull embedding model。
- 不新增 Qdrant dependency、Docker Compose service 或 runtime。
- 不改 `/rag/query` 預設行為。
- 不移除 local keyword RAG baseline。
- 不新增 rerank、hybrid search、eval runner、Redis、NATS、worker、資料庫 schema、登入或 RBAC。
- 不改 OCR provider、PaddleOCR model selection 或 LLM generation path。

## Release Impact

- Target version: `v0.11.0`。
- Version bump required: no。
- 原因：本 ticket 只做 Phase 11 provider decision 與 backlog 文件，不產生 runtime release；版本 bump 留給 Phase 11 完成可驗證 vector indexing / retrieval demo 的 ticket。

## Files likely to change

- `tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] 明確記錄 Phase 11 embedding provider、model、endpoint 與選擇理由。
- [x] 明確記錄 Phase 11 vector store provider、endpoint、collection name 與 payload metadata。
- [x] `TODO.md` 包含 Phase 11 / `v0.11.0` backlog 與本 ticket 完成狀態。
- [x] `docs/ROADMAP.md` 包含 Phase 11 milestone、guardrails 與下一步 ticket 切分。
- [x] 文件明確說明本 ticket 不實作 Qdrant runtime、embedding client、rerank 或 DB。

## Validation

- `rg -n "v0.11.0|phase-11|qwen3-embedding|Qdrant" TODO.md docs/ROADMAP.md tasks/phase-11-vector-rag/11-01-embedding-qdrant-provider-decision.md`
- `git diff --check`
