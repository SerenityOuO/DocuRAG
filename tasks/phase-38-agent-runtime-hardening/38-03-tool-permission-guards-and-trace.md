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

- [ ] Agent tools 有明確 tier 與 permission requirements。
- [ ] Viewer / Analyst / Admin 對 tool execution 的差異由 backend 強制執行。
- [ ] Frontend trace 顯示 permission decision 與 fallback reason。
- [ ] Tests 覆蓋 forbidden tool、allowed tool、invalid plan 與 fallback。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Browser 檢查 Agent trace desktop / mobile。
- `rg -n "tool tier|permission decision|Agent trace|forbidden|fallback|destructive" backend frontend docs TODO.md tasks/phase-38-agent-runtime-hardening`
- `git diff --check`
