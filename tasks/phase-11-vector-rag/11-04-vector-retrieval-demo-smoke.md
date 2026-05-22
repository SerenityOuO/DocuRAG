# 11-04 Vector Retrieval Demo Smoke

## Goal

加入 optional vector retrieval path 與 demo smoke，讓 Phase 11 完成 `v0.11.0` Vector RAG demo release。keyword RAG 仍是 fallback-safe baseline；只有明確設定 vector retrieval provider 時才嘗試 embedding + Qdrant。

## Scope

- 新增 optional vector retrieval path，例如 `DOCURAG_RAG_RETRIEVAL_PROVIDER=vector`。
- 在 query path 中用最小實作把本機 chunks upsert 到 Qdrant，再用 query embedding 做 vector search。
- Qdrant unavailable、embedding unavailable、collection missing 或 vector query failure 時，明確 fallback 到 keyword retrieval。
- fallback 狀態需反映在 citation trace metadata / answer source。
- 保留 existing keyword RAG baseline 與 optional Ollama `qwen3.5:4b` generation path。
- frontend 如需調整，只做最小 answer source / retrieval source / vector fallback 顯示。
- 新增或更新 demo smoke script，驗證 baseline keyword flow 與 optional vector flow。
- 完成 `v0.11.0` release/version sync：
  - backend version
  - frontend package version
  - frontend fallback version
  - health test
  - Docker Compose `DOCURAG_VERSION`
  - `README.md`
  - `backend/README.md`
  - `frontend/README.md`
  - `TODO.md`
  - `docs/ROADMAP.md`

## Out of Scope

- 不實作 rerank。
- 不實作 hybrid search。
- 不實作 eval runner。
- 不新增 Redis、NATS、worker 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 Qdrant 或 Ollama embedding 成為預設必需 runtime。

## Release Impact

- Target version: `v0.11.0`。
- Version bump required: yes。
- 原因：本 ticket 完成 Phase 11 optional Vector RAG demo，需同步 backend/frontend/Compose/health test 與文件 release status。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/api/routes/rag.py`
- `backend/app/services/rag.py`
- `backend/app/services/embedding.py`
- `backend/app/services/vector_store.py`
- `backend/tests/test_rag.py`
- `scripts/demo-smoke-test.ps1`
- `frontend/src/App.vue`
- `frontend/src/api/client.ts`
- `frontend/package.json`
- `frontend/package-lock.json`
- `backend/pyproject.toml`
- `backend/tests/test_health.py`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] 未設定 vector retrieval env 時，`/rag/query` 行為維持 keyword baseline。
- [x] 設定 vector retrieval env 時，backend 會嘗試 embedding + Qdrant vector search。
- [x] vector search 成功時，response trace metadata 顯示 vector retrieval source。
- [x] embedding/Qdrant/collection/vector query 失敗時，response 明確 fallback 到 keyword retrieval，且 demo 不崩潰。
- [x] optional Ollama `qwen3.5:4b` generation path 仍可接在 retrieved chunks 後運作。
- [x] baseline smoke 與 optional vector smoke 可分開執行；若外部 runtime 不可用，文件與 TODO 清楚記錄 mock/unit tests 已覆蓋。
- [x] `v0.11.0` release/version sync 完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- 在 `frontend` 執行 `npm.cmd run build`
- baseline demo smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- optional vector smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunVector`
- `git diff --check`

Result：

- 2026-05-22：backend test script 通過，`84 passed`；本機 PowerShell PATH 需臨時補上 Codex bundled Python 3.12。
- 2026-05-22：`frontend` 的 `npm.cmd run build` 通過。
- 2026-05-22：baseline demo smoke 通過，answer source 為 `deterministic baseline`、retrieval source 為 `keyword baseline`。
- 2026-05-22 follow-up：已在本機準備 Ollama `qwen3-embedding:0.6b` 與 Qdrant，並以 vector-enabled backend 跑通 `scripts/demo-smoke-test.ps1 -RunVector`；answer source 為 `deterministic baseline`，retrieval source 為 `vector/qdrant`。
- 2026-05-22：`git diff --check` 通過。
