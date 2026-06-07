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
- `TODO.md`
- `tasks/phase-36-eval-dashboard-rerank-analysis/36-03-strategy-comparison-and-rerank-analysis.md`

## Acceptance Criteria

- [ ] Eval dashboard 可比較至少 keyword、hybrid_rerank 與一個 optional vector-backed strategy。
- [ ] UI 顯示 Hit Rate@K、MRR@K、Recall@K、latency、failure / fallback counts。
- [ ] Rerank analysis 可顯示 rerank 前後 ranking 與 score。
- [ ] Runtime unavailable 時顯示 fallback，不假裝完整成功。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Retrieval eval dashboard smoke script。
- Browser 檢查 eval dashboard desktop / mobile。
- `rg -n "strategy comparison|hybrid_rerank|rerank score|failure cases|fallback cases|Recall" backend frontend scripts docs TODO.md tasks/phase-36-eval-dashboard-rerank-analysis`
- `git diff --check`
