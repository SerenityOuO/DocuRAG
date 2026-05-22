# 11-02 Ollama Embedding Client

## Goal

新增最小 Ollama embedding provider building block，固定 Phase 11 使用 `qwen3-embedding:0.6b` 與 Ollama native `/api/embed` 的 backend 邊界。此 ticket 預設 disabled，不改 `/rag/query` 預設 keyword baseline，也不接 Qdrant runtime。

## Scope

- 新增 backend embedding provider interface。
- 新增 disabled embedding provider。
- 新增 Ollama embedding provider，使用 native `POST /api/embed`。
- 新增 env 設定：
  - `DOCURAG_EMBEDDING_PROVIDER`
  - `DOCURAG_EMBEDDING_BASE_URL`
  - `DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b`
  - 最小 timeout 設定。
- 補測 successful embed、connection error、HTTP error、timeout、missing model 或 malformed response。
- 若本機 Ollama 與 `qwen3-embedding:0.6b` 可用，用 smoke/helper 固定實際 vector dimension 並更新文件；若不可用，mock tests 需覆蓋核心行為，並在 `TODO.md` / `docs/ROADMAP.md` 記錄限制。

## Out of Scope

- 不新增 Qdrant runtime、Docker Compose service 或 collection helper。
- 不改 `/rag/query` 預設行為。
- 不新增 vector retrieval path。
- 不替換 local keyword RAG baseline。
- 不移除 optional Ollama `qwen3.5:4b` generation path。
- 不新增 rerank、hybrid search、eval runner、Redis、NATS、worker、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。

## Release Impact

- Target version: `v0.11.0`。
- Version bump required: no。
- 原因：本 ticket 只新增 disabled-by-default embedding client building block，尚未完成 Phase 11 vector retrieval demo；版本 bump 留給 `11-04` release sync。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/services/embedding.py`
- `backend/tests/test_embedding.py`
- `scripts/ollama-embedding-smoke.ps1`
- `.env.example`
- `backend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] `DOCURAG_EMBEDDING_PROVIDER` 未設定時，embedding provider 為 disabled，且既有 `/rag/query` keyword baseline 不受影響。
- [x] `DOCURAG_EMBEDDING_PROVIDER=ollama` 時，client 使用 `POST /api/embed` 與 `DOCURAG_EMBEDDING_MODEL=qwen3-embedding:0.6b`。
- [x] tests 覆蓋 successful embed、connection error、HTTP error、timeout 與 malformed response / missing embedding。
- [x] 文件明確說明本 ticket 不啟用 Qdrant、不替換 keyword RAG、不要求本機 Ollama 可用。
- [x] `TODO.md` 與 `docs/ROADMAP.md` 記錄 11-02 完成狀態與本機 model dimension smoke 結果或限制。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `git diff --check`

Result：

- 2026-05-22：backend test script 通過，`70 passed`；本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12。
- 2026-05-22 follow-up：已透過 Ollama API pull `qwen3-embedding:0.6b`；`scripts/ollama-embedding-smoke.ps1` 通過並確認實際 vector dimension 為 `1024`。
- 2026-05-22：`git diff --check` 通過。
