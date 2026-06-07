# Backend Permission Guards

## Goal

將 Phase 32 schema 與 role contract 接到 backend API guard，讓正式 Auth / RBAC 在 backend 層強制執行。

## Scope

- 新增正式 auth dependency / middleware，解析 current user、organization 與 project access。
- 對 document upload、OCR、parse、vector index、eval built-in、Agent run 等 write API 加入 role guard。
- 對 read API 加入 project boundary filter，避免跨 project 查詢。
- 補 backend tests，涵蓋 Viewer forbidden、Analyst allowed、Admin allowed 與 cross-project denied。

## Out of Scope

- 不新增 frontend UI 改版；frontend role surface 留到 `32-04`。
- 不新增 Redis session、SSO、OAuth、MFA 或 audit log pipeline。
- 不修改 RAG ranking、OCR provider、parser provider 或 Agent planner。

## Release Impact

- Target version: `v0.32.0`
- Version bump required: no
- 原因：這是 Phase 32 runtime ticket，版本同步留到 `32-04`。

## Files likely to change

- `backend/app/api/`
- `backend/app/core/`
- `backend/tests/`
- `docs/api.md`
- `TODO.md`
- `tasks/phase-32-auth-rbac-tenant-boundary/32-03-backend-permission-guards.md`

## Acceptance Criteria

- [x] Backend write API 依 role guard 強制拒絕 Viewer。
- [x] Project-scoped read/write API 不能跨 project 存取資料。
- [x] Demo auth mode 與正式 auth mode 都有明確測試。
- [x] Forbidden / unauthorized response 不洩漏跨 tenant 資訊。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "forbidden|permission|project access|Viewer|Analyst|Admin|tenant" backend docs TODO.md tasks/phase-32-auth-rbac-tenant-boundary`
- `git diff --check`

## Validation Result

- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` (`216 passed`, 1 pytest cache warning).
- Passed: `rg -n "forbidden|permission|project access|Viewer|Analyst|Admin|tenant" backend docs TODO.md tasks/phase-32-auth-rbac-tenant-boundary`.
- Passed: `git diff --check` (Windows LF/CRLF warnings only).
