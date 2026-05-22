# 17-04 Trace UI Demo Release Sync

## Goal

完成 `v0.17.0` retrieval trace UI / eval visibility slice 的 demo、文件與 release/version sync，讓 Phase 17 可被重跑驗證。此 ticket 是 Phase 17 的 release ticket，不得加入 `hybrid_rerank` 或 production eval dashboard。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP。
- 補齊 `v0.17.0` Release Status，且 README 只列版本號，不用裸 Phase 條目。
- 執行 backend tests、frontend build、baseline demo smoke、baseline retrieval eval smoke。
- 本機 preflight 可用時，執行 optional vector、`vector_rerank` 與 `hybrid` eval smoke，確認 Phase 17 reporting / trace visibility 沒有破壞 optional paths。
- 明確記錄 production eval dashboard、`hybrid_rerank`、Redis、NATS、worker、DB、auth 與 deployment 留到後續 Phase。

## Out of Scope

- 不實作 `hybrid_rerank`、BM25 dependency、LLM-as-judge、answer faithfulness、citation quality scoring 或 production eval dashboard。
- 不新增 backend API endpoint、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering、production OCR pipeline、Docker service 或 deployment 設定。
- 不 push tag 或建立 release note，除非 ticket 或使用者明確要求 tag。

## Files likely to change

- `backend/pyproject.toml`
- `backend/app/core/config.py`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `scripts/retrieval-eval-smoke.ps1`
- `tasks/phase-17-retrieval-trace-ui/17-04-trace-ui-demo-release-sync.md`

## Acceptance Criteria

- [ ] `v0.17.0` version / docs / TODO / ROADMAP release sync 已完成。
- [ ] README Release Status 只列版本號。
- [ ] Baseline demo smoke 與 baseline retrieval eval smoke 仍可執行。
- [ ] Optional vector / `vector_rerank` / `hybrid` eval smoke 在 local preflight 可用時已重跑或清楚記錄不可用原因。
- [ ] `hybrid_rerank`、production eval dashboard、worker、DB、auth 與 deployment 明確留到後續 Phase。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`（於 `frontend/`）
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional vector / vector_rerank / hybrid eval smoke commands must be run when local preflight is available.
- 若 frontend dev server 可用，使用 Browser 檢查 trace UI。
- `git diff --check`

## Release Impact

- Target version: `v0.17.0`。
- Version bump required: yes。
- 原因：本 ticket 若完成，代表 Phase 17 retrieval trace UI / eval visibility slice 已具備 frontend trace visibility、eval report summary、smoke / docs 與 version sync，需要形成 `v0.17.0` release artifact。
