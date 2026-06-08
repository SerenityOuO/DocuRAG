# Tool Permission Guards and Trace

## Goal

實作 Agent tool permission guards 與完整 planning trace，使 tool-use 可依 role / project / tool tier 安全執行並可被追蹤。

## Scope

- 為現有 Agent tools 標記 tool tier 與 permission requirement。
- 在 Agent run execution 前檢查 role、project access、tool tier 與 side-effect policy。
- Frontend trace 顯示 plan、tool call、permission decision、observation、fallback 與 final answer。
- 補 backend tests 與 frontend build validation。

## Out of Scope

- 不新增 destructive tool execution。
- 不新增任意 SQL、shell、filesystem command 或 external browser/tool access。
- 不修改 Auth / RBAC schema；只使用既有 Phase 32 permission boundary。

## Release Impact

- Target version: `v0.38.0`
- Version bump required: no
- 原因：這是 Phase 38 runtime ticket，版本同步留到 `38-04`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `frontend/src/`
- `docs/api.md`
- `TODO.md`
- `tasks/phase-38-agent-runtime-hardening/38-03-tool-permission-guards-and-trace.md`

## Acceptance Criteria

- [x] Agent tools 有明確 tier 與 permission requirements。
- [x] Viewer / Analyst / Admin 對 tool execution 的差異由 backend 強制執行。
- [x] Frontend trace 顯示 permission decision 與 fallback reason。
- [x] Tests 覆蓋 forbidden tool、allowed tool、invalid plan 與 fallback。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Browser 檢查 Agent trace desktop / mobile。
- `rg -n "tool tier|permission decision|Agent trace|forbidden|fallback|destructive" backend frontend docs TODO.md tasks/phase-38-agent-runtime-hardening`
- `git diff --check`

## Status

- 已完成。
- Agent tools 已標記 `read-only` tier、permission requirement、required roles、side-effect policy 與 human confirmation trace metadata。
- Agent run 在 tool execution 前檢查 role、project context、tool tier 與 side-effect policy；Viewer role 會被 backend guard 擋下，Analyst / Admin 與本地 disabled auth path 只會執行既有 allowlisted read-only tools。
- Frontend Agent trace 顯示 permission decision、阻擋工具、tool tier、side-effect policy 與 fallback reason。
- Validation 已通過：focused Agent tests `17 passed`（1 pytest cache warning）、backend full test `255 passed`（1 pytest cache warning）、frontend build、Chrome GUI Browser check desktop / mobile、ticket `rg` 與 `git diff --check`（僅 Windows LF/CRLF 提示）。
