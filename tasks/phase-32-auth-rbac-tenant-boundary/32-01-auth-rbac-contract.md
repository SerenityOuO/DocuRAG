# Auth RBAC Contract

## Goal

定義 Phase 32 正式 Auth / RBAC / tenant boundary 的最小合約，將 Phase 28 demo auth 升級方向固定下來。

## Scope

- 定義正式使用者、organization、project、role、membership 與 project access 的 domain contract。
- 定義 Viewer、Analyst、Admin 的 backend permission matrix。
- 定義 API guard 原則：哪些 endpoint 需要登入、哪些 write API 需 role guard。
- 定義 demo auth 與正式 auth 的共存 / fallback policy。

## Out of Scope

- 不新增 users / organizations schema 或 migration。
- 不實作正式 login runtime、JWT refresh、Redis session、SSO、OAuth 或 MFA。
- 不修改 frontend role surface 或 backend API runtime。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 32 contract ticket，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-32-auth-rbac-tenant-boundary/32-01-auth-rbac-contract.md`

## Acceptance Criteria

- [ ] 文件列出 role permission matrix，並標示 Viewer / Analyst / Admin 的 API 權限差異。
- [ ] 文件明確定義 organization / project access boundary。
- [ ] 文件說明 demo auth 與正式 auth 的差異，不把 demo auth 說成 production RBAC。
- [ ] 明確標示 SSO / OAuth / MFA / Redis session 不在本 ticket scope。

## Validation

- `rg -n "Auth|RBAC|Viewer|Analyst|Admin|organization|project access|Phase 32" docs README_DEV.md TODO.md tasks/phase-32-auth-rbac-tenant-boundary`
- `git diff --check`
