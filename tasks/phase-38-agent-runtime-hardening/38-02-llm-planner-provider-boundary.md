# LLM Planner Provider Boundary

## Goal

新增 LLM planner provider boundary，讓 Agent 可以在受控情況下產生 task plan，並保留 deterministic fallback。

## Scope

- 實作 LLM planner adapter，輸入 task、allowed tools、role / project context，輸出 validated plan。
- 加入 plan schema validation、timeout、invalid response fallback 與 audit metadata。
- 保留 deterministic planner fallback，且可用 env 明確關閉 LLM planner。
- 補 backend tests，覆蓋 success、timeout、invalid plan 與 fallback。

## Out of Scope

- 不新增任意 tool execution、任意 SQL、shell 或 filesystem access。
- 不允許 destructive tools 自動執行。
- 不修改 RAG retrieval provider 或 parser provider。

## Release Impact

- Target version: `v0.38.0`
- Version bump required: no
- 原因：這是 Phase 38 runtime ticket，版本同步留到 `38-04`。

## Files likely to change

- `backend/app/services/`
- `backend/app/api/`
- `backend/tests/`
- `.env.example`
- `docs/api.md`
- `TODO.md`
- `tasks/phase-38-agent-runtime-hardening/38-02-llm-planner-provider-boundary.md`

## Acceptance Criteria

- [x] LLM planner 可透過 env 明確啟用，預設有 safe fallback。
- [x] Invalid plan 不會執行 tool，會回到 deterministic fallback 或 clear error。
- [x] Backend tests 覆蓋 LLM planner success / failure / fallback。
- [x] Trace metadata 記錄 planner source、fallback reason 與 plan validation result。

## Validation

- [x] `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- [x] `rg -n "LLM planner|deterministic planner|plan validation|fallback|Agent" backend docs TODO.md tasks/phase-38-agent-runtime-hardening`
- [x] `git diff --check`

## Completion Notes

- 新增 `backend/app/services/agent_planner.py`，提供 deterministic planner、LLM planner provider boundary、LLM JSON plan parsing / validation、timeout / unavailable / invalid plan fallback 與 planner audit trace metadata。
- 新增 `DOCURAG_AGENT_PLANNER_PROVIDER` 設定；預設 `deterministic`，只有明確設為 `llm_planner` / `llm` 才會嘗試使用既有 `DOCURAG_LLM_PROVIDER` runtime 產生 plan。
- AgentService 現在先取得 validated plan，再交給既有 allowlisted read-only tools 執行；invalid plan、unknown tool、unsafe route、missing required input 或 timeout 都會在 tool execution 前 fallback。
- Backend tests 已補 LLM planner success、timeout fallback 與 invalid plan fallback，並確認 invalid plan 不會執行 destructive / unknown tool。
- `docs/api.md`、`TODO.md`、`README_DEV.md` 與 `docs/ROADMAP.md` 已同步 38-02 狀態；本 ticket 不 bump version。
- Validation 已通過：focused Agent tests `9 passed`；backend full test `254 passed`（1 pytest cache warning）；ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
