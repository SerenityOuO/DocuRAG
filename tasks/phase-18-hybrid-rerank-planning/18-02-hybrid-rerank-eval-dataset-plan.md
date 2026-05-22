# 18-02 Hybrid Rerank Eval Dataset Plan

## Goal

規劃 future `hybrid_rerank` 評估資料需求，讓後續 implementation 能比較 `hybrid` 與 `hybrid_rerank` 的 Hit Rate@K、MRR@K、Recall@K、latency、fallback count 與 trace metadata，而不在本 ticket 修改 dataset JSON。

## Scope

- 規劃需要新增或標註的 eval case 類型，例如 lexical-heavy、semantic-heavy、branch disagreement、rerank improves ordering 與 rerank fallback。
- 定義後續 dataset update ticket 的驗收方向：case tags、expected document ids、expected evidence、strategy comparison notes。
- 說明 metrics 摘要應沿用既有 eval summary 欄位：`fallback_count`、`trace_metadata_count`、`result_strategy_counts` 與 `fallback_reasons`。
- 只更新 Markdown 規劃文件與 checklist。

## Out of Scope

- 不修改 `sample-data/eval/retrieval-eval.json` 或新增真實資料。
- 不實作 eval runner、`hybrid_rerank` strategy、rerank provider 或 smoke flag。
- 不新增 LLM-as-judge、answer faithfulness、citation quality scoring 或 dashboard。
- 不新增外部依賴、DB schema、worker、auth、deployment 或 Docker service。

## Release Impact

- Target version: `v0.18.0` planning backlog。
- Version bump required: no。
- 原因：本 ticket 只規劃 future eval dataset expansion，不修改 runtime、dataset artifact 或版本化 release 文件。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-18-hybrid-rerank-planning/18-02-hybrid-rerank-eval-dataset-plan.md`

## Acceptance Criteria

- [ ] 已列出 future `hybrid_rerank` dataset case 類型與目的。
- [ ] 已說明後續 dataset ticket 應如何保留公開、可重跑、demo-safe 的資料邊界。
- [ ] 已明確保留既有 eval summary 欄位，不引入新 scoring framework。
- [ ] Release Impact 明確寫 `Version bump required: no` 並說明原因。

## Validation

- `rg -n "v0.18.0|Phase 18|hybrid_rerank|dataset|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md`
- `git diff --check`
