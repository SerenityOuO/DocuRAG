# 25-01 Agent Boundary Contract

## Goal

固定 Phase 25 Agent Tool-use Minimal MVP 的產品與技術邊界，定義 agent run、plan step、tool call、observation、final answer 與 trace metadata；本 ticket 只做規格與文件，不實作 runtime。

## Scope

- 定義 Phase 25 agent MVP 的使用情境：用 structured fields 與 document search 完成 invoice summary / source-backed answer。
- 定義 agent run schema：`run_id`、`status`、`task`、`plan_steps`、`tool_calls`、`final_answer`、`citations`、`trace`、`created_at`、`updated_at`。
- 定義 allowlisted tools：
  - `get_document_fields`
  - `search_documents`
  - `summarize_invoice_fields`
- 定義 deterministic planner 邊界：只針對 demo-safe invoice / document question 產生固定步驟，不接任意工具。
- 定義 future LLM planner / autonomous agent 邊界，但不在 Phase 25 宣稱 production-ready Agent。
- 更新 `docs/api.md`、`docs/architecture.md`、`TODO.md` 與 `docs/ROADMAP.md`。

## Out of Scope

- 不實作 agent runtime、backend API、frontend UI、smoke script 或 storage。
- 不接 LLM autonomous planner、OpenAI function calling、Ollama planning call 或新外部依賴。
- 不允許任意 SQL、任意 tool execution、delete、reindex、file system command、shell command 或 destructive operation。
- 不新增 PostgreSQL、Redis、NATS、worker、async queue、Auth、RBAC、role guard、project permission 或 multi-user isolation。
- 不修改 parser、OCR、RAG retrieval、eval runner、Qdrant indexing 或 default Viewer Chat path。

## Release Impact

- Target version: `v0.25.0` planning backlog。
- Version bump required: no。
- 原因：本 ticket 只固定 Agent contract；Phase 25 runtime 與 release sync 由後續 tickets 完成。

## Files likely to change

- `docs/api.md`
- `docs/architecture.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] 文件明確定義 agent run / step / tool call / observation / final answer schema。
- [ ] 文件明確定義 Phase 25 allowlisted tools 與 deterministic planner 邊界。
- [ ] 文件明確禁止任意 SQL、任意工具執行與破壞性操作。
- [ ] 文件不宣稱已完成 autonomous Agent、正式 RBAC、worker 或 DB-backed tool runtime。

## Validation

- `rg -n "v0.25.0|Phase 25|Agent|tool-use|get_document_fields|search_documents|summarize_invoice_fields|deterministic planner|allowlisted" README.md TODO.md docs/ROADMAP.md docs/api.md docs/architecture.md tasks/phase-25-agent-tool-use-mvp/25-01-agent-boundary-contract.md`
- `git diff --check`
