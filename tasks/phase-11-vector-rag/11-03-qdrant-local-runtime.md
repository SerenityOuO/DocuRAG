# 11-03 Qdrant Local Runtime

## Goal

新增 Qdrant local runtime 與 collection smoke helper，讓 Phase 11 可以在本機建立或檢查 `docurag_chunks_v1` collection。此 ticket 只準備 vector store runtime，不替換 `/rag/query` 預設 keyword RAG。

## Scope

- 更新 Docker Compose，新增 Qdrant service。
- 新增最小 Qdrant settings：
  - `DOCURAG_QDRANT_URL`
  - `DOCURAG_QDRANT_COLLECTION`
  - `DOCURAG_QDRANT_VECTOR_SIZE`
- 新增最小 Qdrant client/helper 或 smoke script，用於建立/檢查 `docurag_chunks_v1` collection。
- collection vector size 來自 11-02 確認的 embedding dimension；若本機模型不可用，使用明確 env/mock default 讓測試可重跑。
- 更新 `.env.example`、README、backend README、ROADMAP 與 TODO 的 Qdrant env / 啟動說明。

## Out of Scope

- 不接 `/rag/query` vector retrieval。
- 不把 backend demo 改成強依賴 Qdrant。
- 不新增 chunk background indexing、worker、Redis、NATS 或 PostgreSQL schema。
- 不新增 rerank、hybrid search、eval runner、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不移除 local keyword RAG baseline 或 optional Ollama `qwen3.5:4b` generation path。

## Release Impact

- Target version: `v0.11.0`。
- Version bump required: no。
- 原因：本 ticket 只新增 optional Qdrant local runtime 與 collection smoke；Phase 11 release/version sync 留給 `11-04`。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/services/vector_store.py`
- `backend/tests/test_vector_store.py`
- `infra/docker-compose.yml`
- `scripts/qdrant-collection-smoke.ps1`
- `.env.example`
- `README.md`
- `backend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] Docker Compose 包含 Qdrant service，且 backend 不因 Qdrant unavailable 無法啟動。
- [x] helper/smoke 可建立或檢查 `docurag_chunks_v1` collection。
- [x] collection vector size 使用明確設定，並記錄與 `qwen3-embedding:0.6b` dimension 的關係。
- [x] tests 用 mock transport 覆蓋 collection exists、create collection、connection failure 與 malformed response。
- [x] 文件說明如何啟動 Qdrant，以及此 ticket 不改 `/rag/query` 預設行為。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- 若 Docker / Qdrant 可用：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\qdrant-collection-smoke.ps1`
- `git diff --check`

Result：

- 2026-05-22：backend test script 通過，`76 passed`；本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12。
- 2026-05-22 follow-up：已啟動 Docker Desktop、用 Docker Compose 啟動 Qdrant，`scripts/qdrant-collection-smoke.ps1` 通過並建立/確認 `docurag_chunks_v1` collection，vector size `1024`、distance `Cosine`。
