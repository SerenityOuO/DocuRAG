# 25-02 Agent Tool Adapters

## Goal

實作 Phase 25 的最小 allowlisted tool adapters，讓 Agent MVP 可以讀取 Phase 24 structured fields、呼叫既有 document search，並產生 deterministic invoice summary。

## Scope

- 新增 agent tool schema 與 service building block。
- 實作 `get_document_fields`：從既有 local JSON metadata store 讀取 document parser result。
- 實作 `search_documents`：使用既有 RAG / keyword retrieval path 查詢文件 chunks，保留 citations / retrieved chunks metadata。
- 實作 `summarize_invoice_fields`：用 deterministic formatter 將 invoice fields 轉成簡短摘要，不呼叫 LLM。
- Tool adapter 必須回傳成功 / 失敗狀態、input summary、output summary 與 trace metadata。
- 新增 backend tests，覆蓋有 fields、缺 parser result、search hit、search miss 與 tool error。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 25-02 狀態。

## Out of Scope

- 不新增 Agent run API；API 留給 `25-03`。
- 不新增 frontend UI；UI 留給 `25-04`。
- 不接 LLM autonomous planner、OpenAI function calling、Ollama planning call 或新外部依賴。
- 不新增任意 SQL、SQL template、PostgreSQL、Redis、NATS、worker、async queue、Auth、RBAC 或 project permission。
- 不修改 parser extraction、OCR provider、RAG ranking、eval runner、Qdrant indexing 或 default Viewer Chat path。
- 不允許 tool 執行 delete、reindex、file system command、shell command 或 destructive operation。

## Release Impact

- Target version: `v0.25.0`。
- Version bump required: no。
- 原因：本 ticket 只新增 Agent tool adapter building block；完整 release sync 由 `25-05` 完成。

## Files likely to change

- `backend/app/schemas/agent.py`
- `backend/app/services/agent_tools.py`
- `backend/app/services/document_storage.py`
- `backend/app/services/rag.py`
- `backend/tests/test_agent_tools.py`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] `get_document_fields` 可讀取已保存的 parser result，缺資料時回傳明確 failure。
- [ ] `search_documents` 可回傳 existing keyword retrieval results 與 citation metadata。
- [ ] `summarize_invoice_fields` 可用 deterministic output 摘要 invoice fields。
- [ ] Tool adapter output 包含 trace metadata，且不執行任何 out-of-scope 操作。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "AgentTool|AgentToolCall|get_document_fields|search_documents|summarize_invoice_fields|agent_tools" backend/app backend/tests TODO.md docs/ROADMAP.md tasks/phase-25-agent-tool-use-mvp/25-02-agent-tool-adapters.md`
- `git diff --check`
