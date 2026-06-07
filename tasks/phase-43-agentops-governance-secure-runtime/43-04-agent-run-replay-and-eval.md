# Agent Run Replay and Eval

## Goal

建立 Agent run replay / eval artifact，讓 tool selection、observation 與 final answer 可以被回放與檢查。

## Scope

- 新增或整理 Agent run trace export / replay format。
- 定義 Agent eval dimensions：tool correctness、permission compliance、evidence coverage、fallback reason 與 final answer groundedness notes。
- 新增 demo-safe replay script / docs / report，依既有 Agent runs 驗證，不執行新的高風險 tool。
- 文件說明 replay 是 deterministic evidence，不是 production autonomous Agent 評測平台。

## Out of Scope

- 不新增 autonomous planner training、不新增 LLM-as-judge、自動修正工具或 production audit storage。
- 不允許 replay 執行 destructive / external side-effect tools。
- 不新增任意 SQL、shell 或 filesystem command tool。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 43 replay / eval artifact ticket，版本同步留到 `43-05`。

## Files likely to change

- `backend/`
- `scripts/`
- `docs/`
- `sample-data/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-43-agentops-governance-secure-runtime/43-04-agent-run-replay-and-eval.md`

## Acceptance Criteria

- [ ] Agent replay artifact 可重現 tool calls、observations、fallback 與 final answer。
- [ ] Agent eval report 至少包含 tool correctness、permission compliance 與 evidence coverage。
- [ ] 文件明確標示 replay 不執行高風險外部副作用。

## Validation

- Agent replay smoke。
- Backend tests if runtime changes。
- `rg -n "Agent replay|tool correctness|permission compliance|evidence coverage|groundedness|fallback reason" backend scripts docs sample-data README_DEV.md TODO.md tasks/phase-43-agentops-governance-secure-runtime`
- `git diff --check`
