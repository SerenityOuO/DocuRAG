# 25-03 Agent Run API

## Goal

新增最小 Agent run API，用 deterministic planner 串接 allowlisted tools，產生可查詢的 plan、tool calls、observations、final answer 與 citations。

## Scope

- 新增 `POST /agent/run`，接收 demo-safe task、可選 `document_id`、可選 query。
- 新增 `GET /agent/runs/{run_id}`，查詢本機保存的 agent run result。
- 實作 deterministic planner：
  - 若 task 涉及 invoice summary，依序呼叫 `get_document_fields`、`search_documents`、`summarize_invoice_fields`。
  - 若必要資料缺失，回傳明確 fallback / failed step，不硬湊答案。
- 將 agent run result 保存到 local JSON metadata store 或既有本機 metadata 結構。
- Agent final answer 必須包含 tool trace 與可用 citations。
- 新增 backend API tests，覆蓋 successful run、missing fields、search fallback、run lookup 與 invalid document。
- 更新 `docs/api.md`、`TODO.md` 與 `docs/ROADMAP.md`。

## Out of Scope

- 不新增 frontend UI；UI 留給 `25-04`。
- 不接 LLM autonomous planner、OpenAI function calling、Ollama planning call、streaming 或新外部依賴。
- 不新增任意 SQL、PostgreSQL、Redis、NATS、worker、async queue、Auth、RBAC、role guard 或 project permission。
- 不執行 delete、reindex、file system command、shell command 或 destructive operation。
- 不修改 parser extraction、OCR provider、RAG ranking、eval runner、Qdrant indexing 或 default Viewer Chat path。

## Release Impact

- Target version: `v0.25.0`。
- Version bump required: no。
- 原因：本 ticket 新增 Agent API slice，但完整 demo / release sync 留給 `25-05`。

## Files likely to change

- `backend/app/api/routes/agent.py`
- `backend/app/api/routes/__init__.py`
- `backend/app/main.py`
- `backend/app/schemas/agent.py`
- `backend/app/services/agent.py`
- `backend/app/services/agent_tools.py`
- `backend/app/services/document_storage.py`
- `backend/tests/test_agent.py`
- `docs/api.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] `POST /agent/run` 可回傳 run id、plan steps、tool calls、final answer 與 citations。
- [ ] `GET /agent/runs/{run_id}` 可查詢保存的 run result。
- [ ] Missing parser fields 或 search miss 會明確記錄 failed / fallback step。
- [ ] Agent run 只使用 allowlisted tools，不執行任意 SQL 或破壞性操作。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `rg -n "/agent/run|/agent/runs|AgentRun|AgentStep|tool_calls|get_document_fields|summarize_invoice_fields" backend/app backend/tests docs/api.md TODO.md docs/ROADMAP.md tasks/phase-25-agent-tool-use-mvp/25-03-agent-run-api.md`
- `git diff --check`
