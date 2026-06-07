# Eval Dataset Management

## Goal

實作 eval dataset / eval item management，讓 Admin / Analyst 可以建立與管理 RAG evaluation dataset。

## Scope

- 新增 eval dataset / eval item backend API 或 DB-backed repository path。
- 支援建立、列表、查看、更新與刪除 eval items 的受控操作。
- Frontend 新增 eval dataset management surface。
- 補 backend tests 與 frontend build validation。

## Out of Scope

- 不實作 strategy comparison dashboard；留給 `36-03`。
- 不新增 LLM-as-judge、answer faithfulness、OCR eval 或 citation quality scoring。
- 不修改 retrieval / rerank runtime behavior。

## Release Impact

- Target version: `v0.36.0`
- Version bump required: no
- 原因：這是 Phase 36 runtime ticket，版本同步留到 `36-04`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `frontend/src/`
- `docs/api.md`
- `TODO.md`
- `tasks/phase-36-eval-dashboard-rerank-analysis/36-02-eval-dataset-management.md`

## Acceptance Criteria

- [x] Admin / Analyst 可管理 eval datasets 與 eval items。
- [x] Viewer 不可建立或修改 eval dataset。
- [x] Backend tests 覆蓋 dataset / item CRUD 與 permission boundary。
- [x] Frontend build 通過且 UI 無 horizontal overflow。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Browser 檢查 eval dataset surface。
- `rg -n "eval dataset|eval item|Hit Rate|MRR|Viewer|Admin|Analyst" backend frontend docs TODO.md tasks/phase-36-eval-dashboard-rerank-analysis`
- `git diff --check`

## Completion Notes

- Backend 新增 `/eval/datasets` 與 `/eval/datasets/{dataset_id}/items` CRUD API，沿用 ingestion guard；Admin / Analyst 可管理，Viewer 在 demo / formal auth write path 會收到 `403 forbidden`。
- Local JSON 與 PostgreSQL metadata repository path 已支援 eval dataset / eval item persistence；dataset delete 會同步刪除其 items。
- Frontend 後台新增 Eval Dataset surface，可建立/更新/刪除 dataset，並管理 query、expected terms、document IDs、chunk IDs、tags 與 notes。
- Validation 已通過：focused backend tests `15 passed`；backend full test `245 passed`；frontend build；Admin API CRUD；Viewer blocked API；Edge headless desktop / mobile DOM surface check；ticket `rg`；`git diff --check`。
- in-app Browser 控制工具因 Node REPL sandbox `spawn setup refresh` 錯誤不可用，本次改用 Edge headless DOM 檢查 eval dataset surface；Edge screenshot flag 未產檔。
- Release Impact：Version bump required: no。版本同步留到 `36-04`；本 ticket 不新增 strategy comparison dashboard、LLM-as-judge、answer faithfulness、OCR eval、citation quality scoring 或 retrieval / rerank runtime behavior。
