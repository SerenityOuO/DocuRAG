# Tool Permission Policy Runtime

## Goal

為 allowlisted Agent tools 加上最小 permission policy runtime，讓 tool call 依 role、project access 與 risk tier 判斷可否執行。

## Scope

- 將既有 allowlisted tools 標示為 read-only / write / admin / destructive tiers。
- 在 Agent run 執行前檢查 user role、project access 與 tool tier。
- 保存 denied tool call 的 generic reason 與 trace metadata，不洩漏 cross-project 資訊。
- 新增測試覆蓋 Viewer / Analyst / Admin 的 tool permission behavior。

## Out of Scope

- 不新增任意 SQL、shell、filesystem command 或 external side-effect tools。
- 不新增 production IAM、SSO、OAuth、MFA 或外部 approval service。
- 不新增 destructive tool runtime；destructive tier 只可作為 policy boundary。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 43 runtime slice，版本同步留到 `43-05`。

## Files likely to change

- `backend/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-43-agentops-governance-secure-runtime/43-02-tool-permission-policy-runtime.md`

## Acceptance Criteria

- [x] Agent tool calls 依 role / project access / tool tier 做 permission check。
- [x] Denied tool call 留下 generic trace，不暴露 unauthorized resource details。
- [x] Backend tests 覆蓋 Viewer / Analyst / Admin tool permission。

## Validation

- Backend targeted tests。
- Backend full test script。
- `rg -n "tool tier|permission|project access|approval_required|denied|destructive" backend docs README_DEV.md TODO.md tasks/phase-43-agentops-governance-secure-runtime`
- `git diff --check`

## Completion Notes

- `backend/app/services/agent_tools.py` 已為既有 read-only Agent tools 補上 `risk_tier`、`risk_score`、`approval_required` 與 `approval_state` policy metadata；不新增任何新 tool。
- `backend/app/services/agent.py` 已在 Agent run-level trace 彙總 risk / approval 狀態；Viewer forbidden path 仍在 tool execution 前停止並留下 generic permission trace。
- `backend/tests/test_agent.py` 與 `backend/tests/test_agent_tools.py` 已補 Viewer / Analyst / Admin permission behavior 與 risk / approval metadata assertions。
- 文件已同步 `docs/architecture.md`、`docs/api.md`、`README_DEV.md`、`TODO.md` 與 `docs/ROADMAP.md`。本 ticket 不 bump version，版本同步留到 `43-05`。
