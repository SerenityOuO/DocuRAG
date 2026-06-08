# Strategy Comparison and Rerank Analysis

## Goal

實作 RAG strategy comparison 與 rerank analysis surface，讓使用者可以量化比較 keyword、vector、hybrid、vector_rerank 與 hybrid_rerank。

## Scope

- 新增 eval run API / service，支援多 strategy comparison。
- Frontend 顯示 metrics table、rerank before / after ranking、failure cases、fallback cases 與 trace metadata coverage。
- 保存 eval run result 與 strategy config。
- 補 backend tests、frontend build 與 eval smoke。

## Out of Scope

- 不新增 LLM-as-judge、answer faithfulness、citation quality scoring 或 production monitoring trend。
- 不更換 default retrieval provider 或 rerank model。
- 不修改 OCR、parser、Agent planner 或 Auth / RBAC policy。

## Release Impact

- Target version: `v0.36.0`
- Version bump required: no
- 原因：這是 Phase 36 runtime ticket，版本同步留到 `36-04`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `frontend/src/`
- `scripts/`
- `docs/api.md`
- `docs/architecture.md`
- `TODO.md`
- `tasks/phase-36-eval-dashboard-rerank-analysis/36-03-strategy-comparison-and-rerank-analysis.md`

## Acceptance Criteria

- [x] Eval dashboard 可跑多策略：keyword、hybrid_rerank 與 optional vector-backed strategy。
- [x] UI 顯示 Hit Rate@K、MRR@K、Recall@K、latency、failure / fallback counts。
- [x] Rerank analysis 可顯示 rerank 前後 ranking 與 score。
- [x] Runtime unavailable 時顯示 fallback，並保留失敗原因。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Retrieval eval dashboard smoke script。
- Browser 驗證 eval dashboard desktop / mobile。
- `rg -n "strategy comparison|hybrid_rerank|rerank score|failure cases|fallback cases|Recall" backend frontend scripts docs TODO.md tasks/phase-36-eval-dashboard-rerank-analysis`
- `git diff --check`

## Status

- Completed strategy comparison eval run API: `POST /eval/runs`, `GET /eval/runs/{run_id}` and `GET /eval/runs/{run_id}/items`.
- Completed eval run persistence for local JSON / PostgreSQL repository paths, including strategy config, metrics summary, case results, failure / fallback cases and rerank analysis payload.
- Completed frontend Strategy comparison panel with metrics table, fallback / failure cases, trace metadata coverage and rerank before / after rank / score visibility.
- Runtime unavailable cases remain visible through fallback cases and fallback reasons instead of being treated as full success.
- Release Impact: Version bump required: no. Version sync remains deferred to `36-04`.

## Validation Result

- `python -m pytest backend/tests/test_evaluation_api.py backend/tests/test_evaluation.py backend/tests/test_repositories.py -q -k "strategy_comparison or hybrid_rerank or local_json_repository_manages_eval_datasets_and_items"`: passed (`8 passed, 26 deselected`, 1 pytest cache warning).
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\eval-dashboard-smoke.ps1`: passed (`7 passed, 27 deselected`, 1 pytest cache warning).
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`: passed (`246 passed`, 1 pytest cache warning).
- `npm.cmd run build`: passed.
- Browser / UI check: in-app Browser remained unavailable because Node REPL sandbox failed with `spawn setup refresh`; fallback Edge headless desktop / mobile screenshot check passed with auth-disabled mock backend and static frontend on `127.0.0.1:5173`.
- Ticket `rg`: passed.
- `git diff --check`: passed.
