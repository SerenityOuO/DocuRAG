# Phase 31 Release Sync

## Goal

完成 Phase 31 `v0.31.0` release sync，將 PostgreSQL / schema / repository foundation 的版本、文件與 validation 紀錄同步完成。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.31.0`。
- 更新 `README.md` 精簡展示重點，更新 `README_DEV.md` 完整 release log。
- 更新 `backend/README.md`、`frontend/README.md`、`TODO.md` 與 `docs/ROADMAP.md`。
- 執行 Phase 31 final validation，記錄 DB-backed mode 與 local JSON fallback 的驗證結果。

## Out of Scope

- 不新增 Phase 32 Auth / RBAC。
- 不新增 Redis、NATS、worker、K8s、vLLM 或 fine-tuning。
- 不修改 OCR、parser、RAG ranking、Agent planner 或 eval dashboard behavior。

## Release Impact

- Target version: `v0.31.0`
- Version bump required: yes
- 原因：Phase 31 完成 DB-backed foundation，屬於 backend architecture 與 demo validation 的明確 release。

## Files likely to change

- `backend/`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/`
- `infra/docker-compose.yml`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-31-enterprise-roadmap/31-05-phase-31-release-sync.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.31.0`。
- [x] README / README_DEV / backend README / frontend README / TODO / ROADMAP 均同步 Phase 31 release 狀態。
- [x] DB-backed mode 與 local JSON fallback validation 均有紀錄。
- [x] 文件明確說明 Phase 31 不等於正式 RBAC、worker pipeline 或 production deployment。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `rg -n "v0.31.0|Phase 31|PostgreSQL|repository|migration|local JSON" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend infra scripts tasks/phase-31-enterprise-roadmap`
- `git diff --check`

## Validation Result

- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` (`205 passed`, 1 pytest cache warning). This includes `/health` version `0.31.0`, local JSON fallback coverage and repository tests for DB-backed mode.
- Passed: `npm.cmd run build` in `frontend/` (`docurag-agentops-frontend@0.31.0`).
- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` against a temporary local backend on port `8017`; health version `0.31.0`, direct text ingestion, parser fields, Agent run and RAG query passed. Qdrant unavailable vector indexing fallback was expected for local baseline.
- Passed: `rg -n "v0.31.0|Phase 31|PostgreSQL|repository|migration|local JSON" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend infra scripts tasks/phase-31-enterprise-roadmap`
- Passed: `git diff --check` (Windows LF/CRLF warnings only).
