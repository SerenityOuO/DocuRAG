# 19-03 Hybrid Rerank Trace Report Sync

## Goal

整理 `hybrid_rerank` trace / report visibility，確保 CLI summary、JSON output 與文件敘事能清楚顯示 hybrid branch merge 與 rerank reordering 的差異。

## Scope

- 檢查 `hybrid_rerank` result JSON 中的 run-level、case-level 與 candidate-level metadata 是否足夠 demo。
- 確保 summary 可統計 `fallback_count`、`fallback_reasons`、`trace_metadata_count` 與 `result_strategy_counts`。
- 視需要補強 metadata naming，避免把 keyword score、vector similarity、merged score 與 rerank score 混成同一種分數。
- 更新 README、backend README、frontend README 或 sample eval README，說明如何解讀 `hybrid_rerank` trace。
- 更新 tests，覆蓋 metadata 欄位與 summary aggregation。

## Out of Scope

- 不新增 frontend production eval dashboard、strategy comparison page、export UI、live eval runner 或 backend API endpoint。
- 不改 `/rag/query` 預設，不讓 `hybrid_rerank` default-on。
- 不新增 BM25、query rewriting、LLM-as-judge、answer faithfulness scoring、citation quality scoring 或外部依賴。
- 不新增 Redis、NATS、worker、PostgreSQL schema、Auth、RBAC、Agent runtime、VLM parser、PDF rendering、production OCR pipeline 或 deployment。

## Release Impact

- Target version: `v0.19.0`。
- Version bump required: no。
- 原因：本 ticket 補齊 `hybrid_rerank` trace / report visibility；完整 release sync 留到 `19-04`。

## Files likely to change

- `backend/app/services/evaluation.py`
- `backend/tests/test_evaluation.py`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `sample-data/eval/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] `hybrid_rerank` JSON output 可區分 branch score、merged score 與 rerank score。
- [ ] Summary 統計包含 fallback count、fallback reasons、trace metadata count 與 result strategy counts。
- [ ] 文件能說清楚 `hybrid_rerank` 是 eval runner strategy，不是 default chat retrieval。
- [ ] Missing metadata behavior 沿用 Phase 17：graceful hidden、`metadata unavailable` 或清楚 fallback state。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybridRerank`
- `rg -n "hybrid_rerank|merged_score|rerank_score|fallback_count|trace_metadata_count" README.md backend/README.md frontend/README.md sample-data/eval/README.md backend/app/services/evaluation.py backend/tests/test_evaluation.py TODO.md docs/ROADMAP.md`
- `git diff --check`
