# Frontend Role Surface and Phase 32 Release Sync

## Goal

完成 Phase 32 `v0.32.0` 的 frontend role surface、文件同步與 final validation，讓正式 Auth / RBAC 成為可展示 release。

## Scope

- 更新 frontend login / role surface，使 Viewer、Analyst、Admin 的可見入口與 backend guard 一致。
- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.32.0`。
- 更新 `README.md`、`README_DEV.md`、backend / frontend README、TODO 與 ROADMAP。
- 執行 final validation：backend tests、frontend build、demo smoke、Browser role checks。

## Out of Scope

- 不新增 SSO、OAuth、MFA、password reset、email verification 或 enterprise identity provider。
- 不新增 Redis session、audit log pipeline、worker queue 或 deployment hardening。
- 不修改 OCR / parser / RAG / Agent 核心行為。

## Release Impact

- Target version: `v0.32.0`
- Version bump required: yes
- 原因：Phase 32 完成正式 Auth / RBAC / tenant boundary，是 user-facing release。

## Files likely to change

- `backend/`
- `frontend/`
- `infra/docker-compose.yml`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `tasks/phase-32-auth-rbac-tenant-boundary/32-04-frontend-role-surface-and-release-sync.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.32.0`。
- [x] Frontend role surface 與 backend permission guard 一致。
- [x] Viewer 不能從 UI 或 API 執行 ingestion / eval / Agent write 操作。
- [x] README 與 README_DEV 清楚說明 Phase 32 不包含 SSO / OAuth / MFA。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Browser 檢查 Admin / Analyst / Viewer role surface 與 mobile / desktop 無 horizontal overflow。
- `rg -n "v0.32.0|Phase 32|Auth|RBAC|Viewer|Analyst|Admin|tenant|project access" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend infra tasks/phase-32-auth-rbac-tenant-boundary`
- `git diff --check`

## Validation Result

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` passed：`216 passed`，1 pytest cache warning。
- `npm.cmd run build` passed。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` passed：health version `0.32.0`，demo flow 通過，Qdrant unavailable fallback 符合預期。
- Browser role checks passed：Admin / Analyst / Viewer desktop 與 mobile surface 均符合角色權限，無 horizontal overflow。
- Viewer API 403 checks passed：Viewer 不能呼叫 ingestion / eval / Agent write API。
- Ticket `rg` passed；`git diff --check` passed（僅 Windows LF/CRLF 提示）。
