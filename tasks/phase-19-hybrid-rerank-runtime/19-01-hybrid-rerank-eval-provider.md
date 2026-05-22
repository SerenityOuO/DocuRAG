# 19-01 Hybrid Rerank Eval Provider

## Goal

實作第一版 disabled-by-default `hybrid_rerank` eval provider，將既有 `hybrid` candidate merge 結果交給既有 rerank service 重新排序，讓 retrieval eval runner 可以比較 `hybrid` 與 `hybrid_rerank`。

## Scope

- 在既有 `backend/app/services/evaluation.py` 中新增 `hybrid_rerank` strategy 的 provider flow。
- 流程固定沿用 Phase 18 planning：keyword branch + optional vector branch -> hybrid merge / dedupe -> optional rerank reordering。
- 重用既有 `HybridEvalProvider` merge / fallback metadata 與既有 `RerankService`，避免新增第二套 rerank abstraction。
- `hybrid_rerank` 必須 explicit opt-in，不得改變 keyword baseline、`vector`、`vector_rerank` 或 `hybrid` 預設行為。
- 新增或更新 backend tests，覆蓋 rerank success、rerank unavailable fallback、vector branch fallback 與 metadata preservation。

## Out of Scope

- 不接 `/rag/query`、frontend live chat、frontend route、production eval dashboard 或 backend API endpoint。
- 不新增 BM25 dependency、query rewriting、score normalization、LLM-as-judge、answer faithfulness scoring 或 citation quality scoring。
- 不新增外部依賴、Docker service、Redis、NATS、worker、PostgreSQL schema、登入、RBAC、Agent runtime、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。
- 不 bump backend / frontend / Docker Compose version；release sync 留到 `19-04`。

## Release Impact

- Target version: `v0.19.0`。
- Version bump required: no。
- 原因：本 ticket 只新增 `hybrid_rerank` eval provider building block；完整 `v0.19.0` release sync 留到 `19-04`。

## Files likely to change

- `backend/app/services/evaluation.py`
- `backend/tests/test_evaluation.py`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] `EvalStrategy` / strategy selection 可識別 `hybrid_rerank`，但預設仍是 `keyword`。
- [ ] `hybrid_rerank` 先產生 hybrid candidates，再只對 hybrid candidates rerank。
- [ ] Rerank success 時輸出 `strategy_label=hybrid_rerank`、rerank score、rerank rank 與 branch / merge metadata。
- [ ] Rerank unavailable 時保留 hybrid candidates，並記錄 `rerank_status` / `rerank_fallback_reason`，不讓 baseline eval 失敗。
- [ ] Vector branch unavailable 時沿用 hybrid keyword-only fallback，不對 missing vector branch 造成 hard failure。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "hybrid_rerank|HybridRerank|rerank_fallback_reason|strategy_label" backend/app/services/evaluation.py backend/tests/test_evaluation.py TODO.md docs/ROADMAP.md`
- `git diff --check`
