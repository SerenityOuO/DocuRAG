# Users Orgs Project Membership Schema

## Goal

新增正式 Auth / RBAC 所需的 users、organizations、projects、roles、memberships 與 project access schema，讓 backend 有可持久化的 multi-user foundation。

## Scope

- 依 Phase 32 contract 建立 users、organizations、projects、roles、memberships / project_memberships schema。
- 定義 password hash / demo seed users / disabled user 的最小欄位。
- 加入 migration 與 backend tests。
- 保留 Phase 28 demo auth mode 作為 explicit demo fallback。

## Out of Scope

- 不接 SSO、OAuth、MFA、external identity provider 或 email verification。
- 不新增 Redis session 或 refresh token rotation。
- 不修改 OCR、parser、RAG、Agent 或 worker pipeline。

## Release Impact

- Target version: `v0.32.0`
- Version bump required: no
- 原因：這是 Phase 32 runtime ticket，版本同步留到 `32-04`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `docs/db-schema.md`
- `.env.example`
- `TODO.md`
- `tasks/phase-32-auth-rbac-tenant-boundary/32-02-users-orgs-project-membership-schema.md`

## Acceptance Criteria

- [x] Migration 建立 users / organizations / projects / roles / memberships 相關 schema。
- [x] Backend tests 驗證基本 user / organization / project membership persistence。
- [x] Demo auth mode 仍可明確啟用，不被靜默替換。
- [x] 文件標示本 ticket 尚未完成所有 endpoint permission guard。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "users|organizations|memberships|roles|project access|DOCURAG_AUTH_MODE" backend docs TODO.md tasks/phase-32-auth-rbac-tenant-boundary`
- `git diff --check`

## Validation Result

- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` (`210 passed`, 1 pytest cache warning).
- Passed: `rg -n "users|organizations|memberships|roles|project access|DOCURAG_AUTH_MODE" backend docs TODO.md tasks/phase-32-auth-rbac-tenant-boundary`.
- Passed: `git diff --check` (Windows LF/CRLF warnings only).
