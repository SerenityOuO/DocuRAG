# Repository Adapter and Migration Path

## Goal

實作 DB-backed repository adapter 與 local JSON migration path，讓 document / chunk / field / eval / agent metadata 可以在 PostgreSQL-backed mode 讀寫。

## Scope

- 新增 PostgreSQL repository implementation，對齊既有 repository interface。
- 新增 migration script / command，將 local JSON demo data 匯入 PostgreSQL-backed store。
- 保留 explicit local JSON fallback / debug mode。
- 補 backend tests，驗證 DB-backed mode 與 fallback mode 的核心讀寫。

## Out of Scope

- 不新增正式 Auth / RBAC / tenant permission enforcement。
- 不新增 Redis、NATS、worker、async queue 或 production deployment。
- 不修改 OCR、parser、RAG ranking、Agent planner 或 eval metric 定義。

## Release Impact

- Target version: `v0.31.0`
- Version bump required: no
- 原因：本 ticket 是 Phase 31 runtime slice；完整 `v0.31.0` release sync 保留給 `31-05`。

## Files likely to change

- `backend/app/repositories/`
- `backend/app/core/`
- `backend/tests/`
- `scripts/`
- `.env.example`
- `docs/architecture.md`
- `TODO.md`
- `tasks/phase-31-enterprise-roadmap/31-04-repository-adapter-and-migration-path.md`

## Acceptance Criteria

- [x] Backend 可透過 env 選擇 local JSON 或 PostgreSQL-backed repository。
- [x] DB-backed repository 支援 documents、chunks、parser fields、eval runs 與 agent runs 的核心讀寫。
- [x] Migration path 可將 local demo metadata 匯入 DB，且不破壞 local demo fallback。
- [x] Backend tests 覆蓋 DB-backed mode 與 fallback mode 的核心讀寫。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "PostgreSQL|repository|migration|local JSON|DOCURAG" backend scripts docs TODO.md tasks/phase-31-enterprise-roadmap`
- `git diff --check`

## Validation Result

- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` (`205 passed`, 1 pytest cache warning)
- Passed: `python -m pytest backend\tests\test_documents.py backend\tests\test_agent.py backend\tests\test_rag.py backend\tests\test_repositories.py -q` (`79 passed`, 1 pytest cache warning)
- Passed: `rg -n "PostgreSQL|repository|migration|local JSON|DOCURAG" backend scripts docs TODO.md tasks/phase-31-enterprise-roadmap`
- Passed: `git diff --check` (Windows LF/CRLF warnings only)
