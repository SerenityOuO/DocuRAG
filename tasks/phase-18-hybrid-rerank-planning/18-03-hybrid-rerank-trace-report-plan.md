# 18-03 Hybrid Rerank Trace Report Plan

## Goal

規劃 future `hybrid_rerank` trace / report visibility，讓後續 implementation 能在 CLI summary、JSON output 與既有 frontend trace panel 中清楚呈現 branch merge 與 rerank 結果，但本 ticket 不修改 UI 或程式碼。

## Scope

- 定義 future report fields：strategy label、branch counts、hybrid merge policy、rerank provider、rerank status、rerank score、fallback reason 與 candidate ordering。
- 規劃 frontend trace panel 後續只讀既有 response / result metadata 的顯示邊界，不新增 live eval dashboard。
- 說明 missing metadata 行為應沿用 Phase 17：graceful hidden、`metadata unavailable` 或清楚 fallback state。
- 只更新 Markdown 規劃文件與 checklist。

## Out of Scope

- 不修改 `frontend/src/App.vue`、CSS、backend eval runner、API response 或 smoke script。
- 不建立 production eval dashboard、strategy comparison page、export UI 或 live eval runner。
- 不實作 `hybrid_rerank`、BM25、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不新增外部依賴、Redis、NATS、worker、DB、auth、RBAC 或 deployment 設定。

## Release Impact

- Target version: `v0.18.0` planning backlog。
- Version bump required: no。
- 原因：本 ticket 只規劃 trace / report display contract，不修改 frontend、backend 或 release artifact。

## Future Visibility Surfaces

後續 `hybrid_rerank` implementation 若接入 eval runner，trace / report visibility 應分成三個層次：

1. CLI summary：提供 demo 口頭講解需要的 strategy、metrics、fallback 與 trace metadata 摘要。
2. JSON output：保留完整 run-level、case-level 與 candidate-level trace metadata，方便後續 README / report 摘錄。
3. Existing frontend trace panel：若後續接入 `/rag/query` 或 result metadata，只能讀既有 response / result 欄位，不新增 live eval dashboard。

## Future Report Fields

run-level fields：

- `strategy_label`
- `candidate_flow`
- `keyword_candidate_count`
- `vector_candidate_count`
- `hybrid_candidate_count`
- `rerank_input_count`
- `final_candidate_count`
- `merge_policy`
- `dedupe_key`
- `dedupe_count`
- `rerank_provider`
- `rerank_model`
- `rerank_status`
- `rerank_latency_ms`
- `fallback_state`
- `fallback_reason`
- `branch_failures`

case-level fields：

- `question`
- `expected_answer`
- `gold_document_id`
- `gold_chunk_ids`
- `result_strategy`
- `hit_at_k`
- `mrr_at_k`
- `recall_at_k`
- `latency_ms`
- `trace_metadata_present`
- `fallback_reason`

candidate-level fields：

- final rank、document id、chunk id、filename、text preview
- branch labels、branch rank、branch score
- merged rank、merged score
- rerank input rank、reranked rank、rerank score
- page / bbox / confidence（若存在）

## Missing Metadata Behavior

後續 UI / report 應沿用 Phase 17 原則：

- 欄位不存在時使用 graceful hidden、`metadata unavailable` 或明確 fallback state。
- optional vector / rerank metadata 缺失不得讓 keyword baseline demo 或 eval summary 失敗。
- branch score、merged score 與 rerank score 不可混成單一分數；若呈現比較，必須標明 score source。
- candidate ordering 應清楚區分 branch rank、merged rank 與 reranked final rank。

## Explicit Non-Goals

- 不建立 production eval dashboard、strategy comparison page、export UI 或 live eval runner。
- 不新增 frontend route、backend endpoint、API response 欄位或 smoke script。
- 不把 `hybrid_rerank` trace 規劃解讀為 runtime 已可用。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-18-hybrid-rerank-planning/18-03-hybrid-rerank-trace-report-plan.md`

## Acceptance Criteria

- [x] 已列出 future `hybrid_rerank` trace / report 欄位。
- [x] 已明確禁止 production eval dashboard 與 live eval runner。
- [x] 已定義 missing metadata / fallback display 原則。
- [x] Release Impact 明確寫 `Version bump required: no` 並說明原因。

## Validation

- `rg -n "v0.18.0|Phase 18|hybrid_rerank|trace|report|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md`
- `git diff --check`
