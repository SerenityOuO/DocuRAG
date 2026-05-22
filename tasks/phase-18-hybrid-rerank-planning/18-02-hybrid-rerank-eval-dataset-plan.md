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

## Planned Dataset Case Types

後續 dataset update ticket 應優先補足能分辨 `hybrid` 與 `hybrid_rerank` 差異的 cases；本 ticket 不修改 JSON，只固定需求。

| Case type | Purpose | Expected signal |
|---|---|---|
| `lexical_heavy` | 問題與正確 chunk 有明確關鍵字重疊，keyword branch 應可穩定召回。 | `hybrid` 不應輸給 keyword baseline，`hybrid_rerank` 不應把正確 chunk 排低。 |
| `semantic_heavy` | 問題使用同義或改寫語句，正確 chunk 需要 vector branch 補召回。 | vector branch 對 Hit Rate@K / Recall@K 有貢獻。 |
| `branch_disagreement` | keyword 與 vector 排名明顯不同，檢查 merge 後 rerank 是否能選出較相關 chunk。 | `hybrid_rerank` 的 MRR@K 應比 `hybrid` 更容易改善。 |
| `rerank_improves_ordering` | 正確 chunk 已在 hybrid candidates 內但排名偏後。 | rerank 後正確 chunk 名次上升，MRR@K 改善。 |
| `rerank_filters_distractor` | 高 lexical / vector score 的近似干擾 chunk 排在前面。 | rerank metadata 應顯示 distractor 被降序。 |
| `rerank_fallback` | reranker disabled / unavailable 時仍可保留 hybrid candidates。 | metrics summary 應反映 fallback，不把 optional failure 算成 dataset failure。 |

## Future Dataset Ticket Acceptance Direction

後續真正修改 dataset 的 ticket 應遵守：

- 只使用公開、虛構、demo-safe 的 sample documents；若既有 sample 不足，先停止並拆新 sample ticket。
- 每筆 case 至少保留 `question`、`expected_answer`、`gold_document_id`、`gold_chunk_ids` 與 metadata tags。
- metadata tags 應包含 case type，例如 `hybrid_rerank`, `branch_disagreement`, `rerank_improves_ordering`。
- 每筆新增 case 應在規劃文字或 metadata notes 中說明 expected evidence 與 strategy comparison note。
- Baseline keyword eval 必須仍可在無 Ollama embedding、Qdrant 或 FastEmbed runtime 時重跑。

## Metrics Summary Boundary

後續 `hybrid_rerank` dataset evaluation 應沿用既有 summary 欄位：

- `fallback_count`
- `trace_metadata_count`
- `result_strategy_counts`
- `fallback_reasons`
- Hit Rate@K、MRR@K、Recall@K、average latency 與 failure count

本 planning 不新增 LLM-as-judge、answer faithfulness、citation quality scoring 或新的 scoring framework。若需要更多 qualitative note，應先放在 dataset metadata / report summary，不改核心 metrics contract。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-18-hybrid-rerank-planning/18-02-hybrid-rerank-eval-dataset-plan.md`

## Acceptance Criteria

- [x] 已列出 future `hybrid_rerank` dataset case 類型與目的。
- [x] 已說明後續 dataset ticket 應如何保留公開、可重跑、demo-safe 的資料邊界。
- [x] 已明確保留既有 eval summary 欄位，不引入新 scoring framework。
- [x] Release Impact 明確寫 `Version bump required: no` 並說明原因。

## Validation

- `rg -n "v0.18.0|Phase 18|hybrid_rerank|dataset|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md`
- `git diff --check`
