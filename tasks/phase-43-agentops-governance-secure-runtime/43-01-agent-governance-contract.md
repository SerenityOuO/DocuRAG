# Agent Governance Contract

## Goal

定義 Phase 43 AgentOps governance / secure tool runtime 邊界，讓 Agent tool-use 具備權限、審計、approval 與 replay 的可展示設計。

## Scope

- 定義 Agent tool tiers：read-only、write、admin、destructive。
- 定義 tool policy、risk score、approval state、audit event 與 replay event 的資料邊界。
- 定義 Agent run trace 必須保留 planning、tool selection、observation、reflection / fallback 與 final answer。
- 固定禁止任意 SQL、shell、filesystem command 或未授權 destructive tool 的原則。

## Out of Scope

- 不新增 runtime tool execution、不新增任意 SQL / shell / filesystem 工具。
- 不新增 production approval workflow、外部 IAM、SSO 或 audit log pipeline。
- 不修改既有 deterministic Agent planner 行為。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 43 governance contract ticket，只定義邊界，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-43-agentops-governance-secure-runtime/43-01-agent-governance-contract.md`

## Acceptance Criteria

- [ ] 文件定義 Agent tool tiers、risk score、approval state、audit event 與 replay event。
- [ ] 文件明確禁止任意 SQL、shell、filesystem command 與未授權 destructive tool。
- [ ] 文件說明 Phase 43 與既有 deterministic Agent MVP 的關係。

## Validation

- `rg -n "Phase 43|Agent governance|tool tiers|approval|audit|replay|destructive|permission" docs README_DEV.md TODO.md tasks/phase-43-agentops-governance-secure-runtime`
- `git diff --check`
