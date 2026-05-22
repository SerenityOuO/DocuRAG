# 12-04 Vector Indexing Demo Smoke

## Goal

補齊 Phase 12 optional vector indexing demo smoke，並完成 `v0.12.0` release/version sync。Demo flow 應明確展示 upload -> OCR -> chunks -> manual vector indexing -> vector retrieval query。

## Scope

- 更新 demo smoke script，讓 optional vector flow 先執行 manual vector indexing，再跑 vector retrieval query。
- Baseline keyword smoke 仍可不依賴 Ollama embedding 或 Qdrant。
- Optional vector smoke 需檢查 Ollama `qwen3-embedding:0.6b`、Qdrant、`docurag_chunks_v1` collection 與 vector indexing API。
- Frontend 若需要，只做最小顯示，例如 vector indexing status 或 retrieval source，不做大改版。
- 文件補齊 Phase 12 demo 指令與 fallback-safe 說明。
- 完成 `v0.12.0` release/version sync：
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
- 不讓 vector retrieval 或 vector indexing 成為 default-on path。

## Release Impact

- Target version: `v0.12.0`。
- Version bump required: yes。
- 原因：本 ticket 完成 Phase 12 optional vector indexing demo，需同步 backend/frontend/Compose/health test 與文件 release status。

## Files likely to change

- `scripts/demo-smoke-test.ps1`
- `scripts/qdrant-collection-smoke.ps1`
- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `frontend/package.json`
- `frontend/package-lock.json`
- `backend/pyproject.toml`
- `backend/app/core/config.py`
- `backend/tests/test_health.py`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] Baseline demo smoke 不依賴 Qdrant 或 embedding，仍通過。
- [x] Optional vector smoke 會先執行 manual vector indexing，再確認 retrieval source 為 `vector/qdrant`。
- [x] Qdrant / embedding unavailable 時，optional vector smoke 以清楚 preflight error 失敗，不影響 baseline demo。
- [x] Frontend 若有調整，只呈現最小 indexing / retrieval 狀態。
- [x] `v0.12.0` release/version sync 完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- 在 `frontend` 執行 `npm.cmd run build`
- baseline demo smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- optional vector indexing smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1 -RunVector`
- `git diff --check`
