# 25-04 Frontend Agent Trace Surface

## Goal

在 demo UI 中新增最小 Agent trace surface，讓 Admin / Analyst 或 developer demo 可以看到 Agent plan、tool calls、observations、final answer 與 citations；Viewer Chat 預設入口仍維持只查詢知識庫。

## Scope

- 在既有 frontend demo 中加入 Agent Tool-use 區塊，位置應屬於 Admin / Analyst / developer-oriented surface，而不是 Viewer Chat 主流程。
- 提供一個 demo-safe task input 或固定範例任務，例如整理 invoice fields 並補充付款期限來源。
- 呼叫 `POST /agent/run`，顯示 plan steps、tool call name、tool status、observation summary、final answer 與 citations。
- 顯示 missing fields / failed tool / fallback 狀態。
- 更新 `frontend/README.md`、`TODO.md` 與 `docs/ROADMAP.md`。

## Out of Scope

- 不新增正式 route、登入、RBAC、role guard、project permission 或 i18n framework。
- 不修改 backend Agent planner / tool adapter 行為。
- 不接 LLM autonomous planner、streaming UI、新外部依賴、Redis、NATS、worker、DB 或 deployment。
- 不讓 Viewer Chat 主流程顯示 upload、OCR、parse 或 Agent operations。
- 不做 production Agent dashboard、任意 tool console 或可編輯 tool registry。

## Release Impact

- Target version: `v0.25.0`。
- Version bump required: no。
- 原因：本 ticket 完成 Phase 25 frontend slice；完整 release sync 留給 `25-05`。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/src/api/client.ts`
- `frontend/src/styles.css`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Viewer Chat 預設入口仍不顯示 upload、OCR、parse 或 Agent operations。
- [ ] Agent trace surface 可顯示 plan、tool calls、observations、final answer 與 citations。
- [ ] Tool failure / fallback state 清楚顯示。
- [ ] UI 不宣稱 production autonomous Agent、正式 RBAC、worker 或 DB runtime。
- [ ] Desktop 與 mobile 檢查無 horizontal overflow。

## Validation

- `npm.cmd run build`
- Browser 檢查 local frontend：Viewer Chat first、Agent trace surface 可用、桌面與手機寬度無 horizontal overflow。
- `rg -n "Agent|tool calls|tool-use|plan|observation|final answer|Agent trace|Viewer Chat" frontend/src frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-25-agent-tool-use-mvp/25-04-frontend-agent-trace-surface.md`
- `git diff --check`
