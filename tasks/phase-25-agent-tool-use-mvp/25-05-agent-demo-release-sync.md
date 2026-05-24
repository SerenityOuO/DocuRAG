# 25-05 Agent Demo Release Sync

## Goal

完成 Phase 25 final validation 與 `v0.25.0` release sync，讓 demo 從 OCR -> structured fields -> RAG 擴充為 OCR -> structured fields -> Agent tool-use -> source-backed final answer 的可展示流程。

## Scope

- 補齊 smoke script 或 demo validation，驗證 upload、OCR、parse、agent run、agent lookup 與 baseline RAG query。
- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `0.25.0`。
- 更新 `README.md`、`backend/README.md`、`frontend/README.md`、`TODO.md`、`docs/ROADMAP.md` 與 `docs/demo-script.md`。
- 記錄 Phase 25 demo 說法：目前是 deterministic planner + allowlisted tools，不是 production autonomous Agent。
- 重跑 backend tests、frontend build、baseline demo smoke、Browser 檢查與必要 `rg` / `git diff --check`。

## Out of Scope

- 不新增 LLM autonomous planner、OpenAI function calling、Ollama planning call、streaming agent 或新外部依賴。
- 不新增任意 SQL、PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、Agent permission model、K8s 或 deployment 設定。
- 不執行 delete、reindex、file system command、shell command 或 destructive operation。
- 不修改 parser extraction、OCR provider、RAG ranking、eval runner、Qdrant indexing 或 default Viewer Chat path。
- 不建立 release tag。

## Release Impact

- Target version: `v0.25.0`。
- Version bump required: yes。
- 原因：Phase 25 完成 Agent boundary contract、tool adapters、Agent run API、frontend trace surface 與 demo validation 後，形成新的 Agent Tool-use Minimal MVP release artifact。

## Files likely to change

- `backend/pyproject.toml`
- `backend/app/core/config.py`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/api/client.ts`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `docs/demo-script.md`
- `scripts/demo-smoke-test.ps1`

## Acceptance Criteria

- [ ] Backend / frontend / Docker Compose / health test versions 同步到 `0.25.0`。
- [ ] Demo smoke 可驗證 parser 後 agent run 與 agent lookup。
- [ ] README 與 demo script 說明 Agent tool-use demo，且不宣稱 production autonomous Agent。
- [ ] Phase 25 TODO、ROADMAP 與 ticket 狀態同步完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Browser 檢查 local frontend：Viewer Chat first、Agent trace surface、桌面與手機寬度無 horizontal overflow。
- `rg -n "v0.25.0|Phase 25|Agent|tool-use|get_document_fields|search_documents|summarize_invoice_fields|deterministic planner|allowlisted" README.md backend/README.md frontend/README.md docs/demo-script.md docs/ROADMAP.md TODO.md backend/app frontend/src tasks/phase-25-agent-tool-use-mvp`
- `git diff --check`
