# 16-04 Hybrid Demo Release Sync

## Goal

補齊 optional `hybrid` retrieval eval smoke、文件與 `v0.16.0` release/version sync，讓 Phase 16 hybrid retrieval slice 可被重跑驗證。此 ticket 是 Phase 16 的 release ticket；不得加入 `hybrid_rerank` 或 frontend trace UI。

## Scope

- 更新 demo / eval smoke documentation 或 script flag，展示 baseline keyword、optional vector、optional `vector_rerank` 與 optional `hybrid` comparison。
- 執行 backend tests、baseline demo smoke、baseline eval smoke，並在 local preflight 可用時執行 optional vector / vector_rerank / hybrid eval smoke。
- 同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP。
- 記錄 `v0.16.0` Release Status，且 README 只列版本號，不用裸 Phase 條目。
- 明確記錄 frontend trace UI、`hybrid_rerank`、Redis、NATS、worker、DB、auth 與 production deployment 留到後續 Phase。

## Out of Scope

- 不實作 `hybrid_rerank`、BM25 dependency、LLM-as-judge、answer faithfulness、citation quality scoring 或 eval dashboard。
- 不新增 frontend trace UI、API endpoint、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering、production OCR pipeline、Docker service 或 deployment 設定。
- 不 push tag 或建立 release note，除非 ticket 或使用者明確要求 tag。

## Release Impact

- Target version: `v0.16.0`。
- Version bump required: yes。
- 原因：本 ticket 若完成，代表 Phase 16 hybrid retrieval slice 已具備 dataset expansion、optional hybrid eval strategy、smoke / docs 與 version sync，需要形成 `v0.16.0` release artifact。

## Files likely to change

- `backend/pyproject.toml`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/App.vue`
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
- [ ] Optional `hybrid` eval smoke 有明確 preflight、env 與 fallback 行為。
- [ ] `v0.16.0` version / docs / TODO / ROADMAP release sync 已完成。
- [ ] README Release Status 只列版本號。
- [ ] `hybrid_rerank`、frontend trace UI、worker、DB、auth 與 deployment 明確留到後續 Phase。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`（於 `frontend/`，若 frontend files changed）
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional vector / vector_rerank / hybrid eval smoke commands must be run when local preflight is available.
- `git diff --check`
