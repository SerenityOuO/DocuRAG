# Agent Runtime Permission Contract

## Goal

定義 Phase 38 Agent runtime hardening 的 planner、tool permission、trace 與 fallback contract，讓 Agent 從 deterministic MVP 前進到可控的 task planning runtime。

## Scope

- 定義 Agent planner boundary：deterministic fallback、LLM planner provider、timeout 與 invalid plan fallback。
- 定義 tool tiers：read-only、write、admin、destructive。
- 定義 tool permission guard、project access check、human confirmation requirement 與 trace fields。
- 更新 docs、TODO、ROADMAP 與 README_DEV。

## Out of Scope

- 不新增 LLM planner runtime 或 tool execution code。
- 不允許任意 SQL、shell、filesystem command、network tool 或 destructive tool。
- 不修改 Auth / RBAC schema、RAG ranking、OCR 或 parser behavior。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 38 contract ticket，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-38-agent-runtime-hardening/38-01-agent-runtime-permission-contract.md`

## Acceptance Criteria

- [x] 文件定義 deterministic fallback 與 LLM planner provider boundary。
- [x] Tool tiers 與 permission guards 清楚。
- [x] Trace contract 包含 plan、tool selection、observation、reflection / fallback 與 final answer。
- [x] 文件明確禁止任意 SQL / shell / filesystem / destructive tools。

## Validation

- [x] `rg -n "Agent|planner|tool permission|read-only|destructive|fallback|Phase 38" docs README_DEV.md TODO.md tasks/phase-38-agent-runtime-hardening`
- [x] `git diff --check`

## Completion Notes

- `docs/architecture.md` 與 `docs/api.md` 已定義 Phase 38 Agent runtime permission contract：`deterministic` planner 是 always-available fallback，future `llm_planner` 必須輸出 validated structured plan，timeout / invalid plan / unsafe tool selection / missing evidence 皆不得執行 unsafe tool。
- Tool tiers 已固定為 `read-only`、`write`、`admin`、`destructive`，permission guard 必須檢查 role、project access、tool allowlist、tool tier、input schema、target resource project 與 human confirmation state。
- Trace contract 已涵蓋 plan、tool selection、permission decision、observation、reflection / fallback 與 final answer，並禁止保存 production secret、raw bearer token、API key 或 private credential。
- 文件已明確禁止任意 SQL、shell、filesystem command、arbitrary network tool、delete、drop table、destructive reindex、credential mutation、production database mutation 或任何 destructive tool。
- `TODO.md`、`README_DEV.md` 與 `docs/ROADMAP.md` 已同步狀態；本 ticket 不 bump version、不新增 runtime code。
