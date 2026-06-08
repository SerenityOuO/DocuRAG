# Chunking Indexing Ablation Report

## Goal

建立 chunking / indexing 策略比較報告，展示 fixed-size、semantic、parent-child 或 indexing policy 對檢索品質的影響。

## Scope

- 補充 ablation report 文件或 artifact template。
- 比較至少兩種 chunking / indexing policy 的預期差異與 metrics 欄位。
- 說明 Qdrant payload filter、payload index、stale vector cleanup 與 reindex 對品質與延遲的影響。
- 將結果連回 Phase 35 / Phase 36 / Phase 41 的 eval metrics。

## Out of Scope

- 不新增新的 chunking runtime，除非 Phase 35 已完成且本 ticket 只讀取既有輸出。
- 不新增 Qdrant production tuning、BM25 dependency、query rewriting 或 LLM-as-judge。
- 不宣稱沒有實測的策略勝率。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 41 analysis artifact ticket，版本同步留到 `41-05`。

## Files likely to change

- `docs/`
- `sample-data/eval/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-41-rag-quality-regression-datasetops/41-04-chunking-indexing-ablation-report.md`

## Acceptance Criteria

- [x] Ablation report 說明至少兩種 chunking / indexing policy 的比較方式。
- [x] Report 包含 Hit Rate@K、MRR@K、Recall@K、latency 與 fallback 欄位。
- [x] 文件說明哪些結果是實測、哪些只是待測假設。

## Validation

- `rg -n "ablation|chunking|fixed-size|semantic|parent-child|payload index|stale vector|reindex" docs sample-data README_DEV.md TODO.md tasks/phase-41-rag-quality-regression-datasetops`
- `git diff --check`

## Completion Notes

- 新增 `docs/chunking-indexing-ablation-report.md`，把 fixed-size、semantic、parent-child、Qdrant payload filter / payload index、stale vector cleanup 與 reindex 連回 Phase 35 / Phase 36 / Phase 41 eval metrics。
- 新增 `sample-data/eval/chunking-indexing-ablation-template.json`，固定 ablation artifact 欄位與 `measured` / `pending_hypothesis` / `not_supported` evidence status。
- 目前只把 Phase 41 keyword regression baseline 標成實測；fixed-size、semantic、parent-child 與 indexing policy rows 都不宣稱勝率。
