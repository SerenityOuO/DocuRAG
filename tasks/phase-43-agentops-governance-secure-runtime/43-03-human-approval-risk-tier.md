# Human Approval Risk Tier

## Goal

新增 human approval / risk tier 的 demo-safe 設計與最小狀態，使高風險 Agent tool call 不會被靜默執行。

## Scope

- 定義 approval states：not_required、required、approved、rejected、expired。
- 對 write / admin / destructive tier tool call 設計 approval_required trace。
- 可新增 demo-safe approval API 或文件化狀態模型，依 ticket scope 選擇最小可驗證做法。
- 補充 UI / API / trace 中如何呈現等待 approval 與 rejected state。

## Out of Scope

- 不新增 production workflow engine、通知系統、Slack / email integration 或外部審批平台。
- 不執行 destructive action，不新增資料刪除工具。
- 不繞過既有 RBAC / project access guard。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 43 approval evidence ticket，版本同步留到 `43-05`。

## Files likely to change

- `backend/`
- `frontend/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-43-agentops-governance-secure-runtime/43-03-human-approval-risk-tier.md`

## Acceptance Criteria

- [x] Risk tier 與 approval state 在文件、API 或 trace 中可驗證。
- [x] 高風險 tool call 不會靜默執行。
- [x] Validation 覆蓋 approval required / approved / rejected 或 skip-safe path。

## Validation

- Backend tests。
- Frontend build if UI changes。
- Agent approval smoke or trace validation。
- `rg -n "approval|required|approved|rejected|expired|risk tier|human approval" backend frontend docs README_DEV.md TODO.md tasks/phase-43-agentops-governance-secure-runtime`
- `git diff --check`

## Completion Notes

- `AgentToolPolicy.approval_state` 已固定為 `not_required`、`required`、`approved`、`rejected`、`expired`。
- `approval_required=true` 且狀態不是 `approved` 時，permission evaluator 會 fail closed，並在 trace metadata 輸出 `approval_required`、`approval_rejected` 或 `approval_expired`。
- `approved` 仍只代表 approval gate 通過；role、project access、tool tier、side-effect policy 與 destructive boundary 仍會先行檢查。
- 目前 allowlisted Agent runtime tools 仍維持 read-only / `not_required`；本 ticket 沒有新增 UI、approval API、外部 workflow 或 destructive tool。
