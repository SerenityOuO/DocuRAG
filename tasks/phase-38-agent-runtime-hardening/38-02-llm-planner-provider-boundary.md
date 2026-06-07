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

- [ ] LLM planner 可透過 env 明確啟用，預設有 safe fallback。
- [ ] Invalid plan 不會執行 tool，會回到 deterministic fallback 或 clear error。
- [ ] Backend tests 覆蓋 LLM planner success / failure / fallback。
- [ ] Trace metadata 記錄 planner source、fallback reason 與 plan validation result。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "LLM planner|deterministic planner|plan validation|fallback|Agent" backend docs TODO.md tasks/phase-38-agent-runtime-hardening`
- `git diff --check`
