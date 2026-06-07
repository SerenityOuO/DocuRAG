# Repository Adapter and Migration Path

## Goal

實作 DB-backed repository 的最小 adapter 與 local JSON migration path，讓核心 document / chunk / field / eval / agent metadata 可以在 PostgreSQL-backed mode 下讀寫。

## Scope

- 新增 PostgreSQL repository implementation，對齊既有 repository interface。
- 新增 migration script 或 command，將既有 local JSON demo data 匯入 PostgreSQL-backed store。
- 保留 explicit local JSON fallback / debug mode。
- 補 backend tests，驗證 DB-backed mode 與 fallback mode 的核心讀寫行為。

## Out of Scope

- 不新增正式 Auth / RBAC 或 tenant permission enforcement。
- 不新增 Redis、NATS、worker、async queue 或 production deployment。
- 不改 OCR、parser、RAG ranking、Agent planner 或 eval metric 定義。

## Release Impact

- Target version: `v0.31.0`
- Version bump required: no
- 原因：這是 Phase 31 runtime ticket，但版本同步只在 `31-05` release sync ticket 完成。

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

- [ ] Backend 可透過 env 選擇 local JSON 或 PostgreSQL-backed repository。
- [ ] DB-backed repository 支援 documents、chunks、parser fields、eval runs 與 agent runs 的既有核心操作。
- [ ] migration path 可將 local demo metadata 匯入 DB，且不破壞既有 local demo fallback。
- [ ] Backend tests 覆蓋 DB-backed mode 與 fallback mode 的主要讀寫行為。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "PostgreSQL|repository|migration|local JSON|DOCURAG" backend scripts docs TODO.md tasks/phase-31-enterprise-roadmap`
- `git diff --check`
