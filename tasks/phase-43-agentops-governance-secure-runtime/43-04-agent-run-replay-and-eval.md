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

- [x] Agent replay artifact 可重現 tool calls、observations、fallback 與 final answer。
- [x] Agent eval report 至少包含 tool correctness、permission compliance 與 evidence coverage。
- [x] 文件明確標示 replay 不執行高風險外部副作用。

## Validation

- Agent replay smoke。
- Backend tests if runtime changes。
- `rg -n "Agent replay|tool correctness|permission compliance|evidence coverage|groundedness|fallback reason" backend scripts docs sample-data README_DEV.md TODO.md tasks/phase-43-agentops-governance-secure-runtime`
- `git diff --check`

## Completion Notes

- 新增 `sample-data/eval/agent-replay-sample.json` 作為 inspection-only replay artifact，保存 policy snapshot、plan steps、tool calls、observations、citations、fallback reason 與 final answer source。
- 新增 `scripts/agent-replay-smoke.ps1`，只讀 replay artifact 並產生 deterministic report，不呼叫 backend API、不重新執行 Agent tool、不連線外部服務。
- 新增 `sample-data/eval/agent-replay-report.json`，包含 tool correctness、permission compliance、evidence coverage、fallback reason 與 groundedness notes。
- 本 ticket 未改 backend runtime，因此不需要 backend tests；版本同步留到 `43-05`。
