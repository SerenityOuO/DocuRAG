# 16-02 Eval Dataset Expansion JSON

## Goal

依 Phase 14 dataset expansion plan，擴充公開 retrieval eval dataset，讓後續 `hybrid` strategy 有更能區分 keyword、vector、rerank 與 hybrid retrieval 品質的 cases。此 ticket 才允許修改 dataset JSON，但不得新增 sample documents 或 runtime。

## Scope

- 擴充 `sample-data/eval/retrieval-eval.json`，使用既有公開虛構 sample documents 建立更多 eval cases。
- 新增或整理 tags / metadata，覆蓋 lexical mismatch、multi-evidence、near-duplicate chunks、cross-document ambiguity、numeric / table lookup 等 case type。
- 讓 dataset 總 cases 數至少達到 `12`，並保持既有 schema 向後相容。
- 若新增 metadata 欄位，補齊必要的 schema / runner 測試，確保 baseline keyword eval 仍可執行。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 16 dataset expansion 狀態。

## Out of Scope

- 不新增 sample documents、PDF、image、真實個資、真實合約或敏感業務資料。
- 不實作 hybrid retrieval runtime、BM25、rerank、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不新增 API endpoint、frontend UI、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不修改 production storage，不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 eval runner、vector retrieval、rerank 或 hybrid strategy 成為 default-on path。

## Release Impact

- Target version: `v0.16.0`。
- Version bump required: no。
- 原因：本 ticket 只擴充公開 eval dataset 與必要測試，Phase 16 release/version sync 留到 `16-04`。

## Files likely to change

- `sample-data/eval/retrieval-eval.json`
- `backend/tests/test_evaluation.py`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-16-hybrid-retrieval/16-02-eval-dataset-expansion-json.md`

## Acceptance Criteria

- [ ] Dataset 總 cases 數至少為 `12`。
- [ ] 新增 cases 至少覆蓋 lexical mismatch、multi-evidence、near-duplicate chunks、cross-document ambiguity 與 numeric / table lookup 中的四類。
- [ ] Dataset 仍只使用公開虛構資料，且不新增 sample documents。
- [ ] Baseline keyword retrieval eval smoke 仍可執行。
- [ ] 必要測試已覆蓋 dataset schema 或 runner 相容性。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- `git diff --check`
