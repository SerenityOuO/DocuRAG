# 15-04 Rerank Demo Release Sync

## Goal

補齊 disabled-by-default `vector_rerank` demo smoke、文件與 `v0.15.0` release/version sync，讓 rerank runtime spike 可被重跑驗證。此 ticket 是 Phase 15 的 release ticket；不得引入 hybrid search。

## Scope

- 更新 demo / eval smoke documentation 或 script flag，展示 baseline keyword、optional vector 與 optional `vector_rerank` comparison。
- 執行 backend tests、baseline demo smoke、baseline eval smoke 與 optional rerank eval smoke。
- 同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP。
- 記錄 `v0.15.0` Release Status，且 README 只列版本號，不用裸 Phase 條目。
- 明確記錄 hybrid search、dataset expansion JSON 與 frontend trace UI 留到後續 Phase。

## Out of Scope

- 不實作 hybrid search、BM25、score fusion 或 merge / dedupe policy。
- 不新增 eval dataset JSON、sample documents、API endpoint、frontend trace UI、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不 push tag 或建立 release note，除非 ticket 或使用者明確要求 tag。

## Release Impact

- Target version: `v0.15.0`。
- Version bump required: yes。
- 原因：本 ticket 若完成，代表 Phase 15 disabled-by-default `vector_rerank` runtime spike 已具備 demo / eval smoke 與文件同步，需要形成 `v0.15.0` release artifact。

## Files likely to change

- `backend/pyproject.toml`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/api/client.ts`
- `backend/tests/test_health.py`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `scripts/retrieval-eval-smoke.ps1`

## Acceptance Criteria

- [ ] Baseline keyword demo / eval smoke 仍可執行。
- [ ] Optional `vector_rerank` eval smoke 有明確 preflight、env 與 fallback 行為。
- [ ] `v0.15.0` version / docs / TODO / ROADMAP release sync 已完成。
- [ ] README Release Status 只列版本號。
- [ ] Hybrid search 與 dataset JSON expansion 明確留到後續 Phase。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`（於 `frontend/`，若 frontend files changed）
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional `vector_rerank` eval smoke command must be run when local rerank provider preflight is available.
- `git diff --check`

