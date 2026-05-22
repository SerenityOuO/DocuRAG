# 13-04 Retrieval Evaluation Demo Smoke

## Goal

補齊 Phase 13 retrieval evaluation demo smoke，並完成 `v0.13.0` release/version sync。Demo flow 應清楚展示 baseline keyword eval 與 optional vector eval 的 metrics，而不是只看單次 RAG query。

## Scope

- 更新 demo / eval smoke 指令與文件，讓使用者能重跑 retrieval evaluation baseline。
- Baseline eval smoke 不依賴 Ollama embedding 或 Qdrant。
- Optional vector eval smoke 需檢查 Ollama `qwen3-embedding:0.6b`、Qdrant、`docurag_chunks_v1` collection、manual vector indexing API。
- 文件補齊 Phase 13 demo 指令、metrics 說明與 fallback-safe 說明。
- Frontend 若需要，只做最小顯示，例如 link / note，不做 eval dashboard。
- 完成 `v0.13.0` release/version sync：
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
- 不實作 LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不新增 Redis、NATS、worker 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 eval runner、vector retrieval 或 vector indexing 成為 default-on path。

## Release Impact

- Target version: `v0.13.0`。
- Version bump required: yes。
- 原因：本 ticket 完成 Phase 13 retrieval evaluation baseline demo，需同步 backend/frontend/Compose/health test 與文件 release status。

## Files likely to change

- `scripts/retrieval-eval-smoke.ps1`
- `scripts/demo-smoke-test.ps1`
- `frontend/src/App.vue`
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

- [ ] Baseline retrieval eval smoke 不依賴 Qdrant 或 embedding，仍通過。
- [ ] Optional vector retrieval eval smoke 會先完成 manual vector indexing，再輸出 vector metrics。
- [ ] Eval output 包含 per-query results 與 summary metrics。
- [ ] Qdrant / embedding unavailable 時，optional vector eval smoke 以清楚 preflight error 失敗，不影響 baseline eval。
- [ ] `v0.13.0` release/version sync 完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- 在 `frontend` 執行 `npm.cmd run build`
- baseline demo smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- baseline retrieval eval smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- optional vector retrieval eval smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVector`
- `git diff --check`
