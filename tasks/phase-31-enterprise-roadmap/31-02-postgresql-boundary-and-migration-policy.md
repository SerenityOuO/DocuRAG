# PostgreSQL Boundary and Migration Policy

## Goal

定義 Phase 31 的 PostgreSQL 邊界、migration policy 與 local JSON fallback / migration path，讓後續 DB schema 與 repository ticket 有明確前提。

## Scope

- 盤點目前 local JSON store 保存的 documents、OCR results、chunks、parser fields、eval runs 與 agent runs。
- 定義 PostgreSQL 採用方式、migration 工具選型、migration 命名規則與 rollback 原則。
- 定義 demo fallback：何時仍可使用 local JSON，何時必須走 DB-backed store。
- 更新開發文件與 architecture / roadmap 中的 Phase 31 DB 邊界。

## Out of Scope

- 不新增實際 PostgreSQL schema 或 migration 檔。
- 不改 backend runtime repository 或 API 行為。
- 不新增正式 Auth / RBAC、Redis、NATS、worker、K8s 或 deployment 設定。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 31 contract ticket，只定義 DB 邊界與 migration policy，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/db-schema.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-31-enterprise-roadmap/31-02-postgresql-boundary-and-migration-policy.md`

## Acceptance Criteria

- [x] 文件明確列出目前 local JSON store 的資料類型與對應 DB domain。
- [x] migration policy 包含命名規則、執行方式、rollback / downgrade 原則與 validation 方法。
- [x] 文件說明 local JSON fallback / migration path，不讓 Phase 31 一次切斷現有 demo。
- [x] 明確標示本 ticket 不新增 schema、repository runtime 或正式 RBAC。

## Validation

- `rg -n "PostgreSQL|migration|local JSON|fallback|Phase 31" docs README_DEV.md TODO.md tasks/phase-31-enterprise-roadmap`
- `git diff --check`

## Validation Result

- Passed: `rg -n "PostgreSQL|migration|local JSON|fallback|Phase 31" docs README_DEV.md TODO.md tasks/phase-31-enterprise-roadmap`
- Passed: `git diff --check`（僅 Windows LF/CRLF 提示）
