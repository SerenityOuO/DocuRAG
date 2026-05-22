# 18-01 Hybrid Rerank Boundary Contract

## Goal

規劃 Phase 18 的 `hybrid_rerank` 邊界，明確定義它和既有 `keyword`、`vector`、`vector_rerank`、`hybrid` 的關係，避免後續 implementation 同時擴張 retrieval、rerank、dashboard 或 infra scope。

## Scope

- 文件化 `hybrid_rerank` 的 candidate flow：keyword branch + vector branch 先合併為 hybrid candidates，再交給 optional reranker 重新排序。
- 定義第一版 strategy label、fallback states、provider metadata、candidate count 與 branch trace 欄位需求。
- 明確寫出後續 implementation 必須 disabled-by-default，且不得改變 baseline keyword demo。
- 只更新 Markdown 規劃文件與 checklist。

## Out of Scope

- 不實作 `hybrid_rerank` runtime、score fusion code、BM25 dependency、rerank invocation 或 backend API。
- 不改 `/rag/query`、frontend UI、eval runner、sample dataset 或 smoke script。
- 不新增外部依賴、Docker service、Redis、NATS、worker、DB、auth、RBAC 或 deployment 設定。
- 不做 LLM-as-judge、answer faithfulness、citation quality scoring 或 production eval dashboard。

## Release Impact

- Target version: `v0.18.0` planning backlog。
- Version bump required: no。
- 原因：本 ticket 只建立 Phase 18 邊界 contract 與 guardrails，不產生 runtime release artifact；後續 implementation 已排入 Phase 19，才由 release sync ticket bump 到 `v0.19.0`。

## Planned Boundary Contract

`hybrid_rerank` 是 future optional strategy，不取代既有 baseline。第一版候選流程固定如下：

1. keyword branch 產生 lexical candidates，沿用既有 keyword scoring 與 citation metadata。
2. vector branch 在 explicit vector-enabled runtime 可用時產生 semantic candidates；若 provider disabled、preflight 失敗或 collection 不可用，必須記錄 branch failure。
3. hybrid merge 依既有 `hybrid` plan 做 deterministic rank-based merge / dedupe，輸出 hybrid candidates。
4. rerank step 只接收 hybrid candidates，使用 disabled-by-default reranker 重新排序，輸出 final `hybrid_rerank` candidates。
5. 任一 optional branch 或 reranker 不可用時，必須 fallback 到可解釋的前一階段 candidates，不得讓 keyword baseline demo 失敗。

第一版 strategy label 固定為 `hybrid_rerank`。它只應在後續 ticket 明確要求時接入 eval runner / smoke flag，且必須保持 explicit opt-in；不得變成 `/rag/query`、frontend demo 或 baseline eval 的預設策略。

## Required Trace Metadata

後續 implementation 至少需要保留下列 run-level metadata：

- `strategy_label`: `hybrid_rerank`
- `candidate_flow`: `keyword+vector -> hybrid_merge -> rerank`
- `keyword_candidate_count`、`vector_candidate_count`、`hybrid_candidate_count`、`rerank_input_count`、`final_candidate_count`
- `merge_policy` 與 `dedupe_key`
- `rerank_provider`、`rerank_model`、`rerank_status`、`rerank_top_k`、`rerank_latency_ms`
- `fallback_state`、`fallback_reason`、`branch_failures`

candidate-level metadata 至少需要保留：

- original branch labels、branch rank、branch score
- merged rank、merged score
- original rerank input rank、reranked rank、rerank score
- document / chunk / citation metadata：`document_id`、`chunk_id`、`filename`、page / bbox / confidence（若存在）

## Fallback States

後續 implementation 應清楚區分以下 fallback states：

- `none`: keyword、vector、merge 與 rerank 都成功。
- `vector_unavailable`: vector branch disabled、preflight failed、Qdrant unavailable 或 embedding unavailable；結果可退回 keyword-only hybrid candidates。
- `vector_empty`: vector branch 成功但沒有候選；結果可退回 keyword candidates，並保留 empty branch metadata。
- `merge_dedupe_partial`: dedupe key 缺少 `chunk_id` 或 citation metadata，只能使用 fallback key；不得靜默丟失候選。
- `reranker_disabled`: reranker provider 未啟用；保留 hybrid candidates 與 rerank skipped metadata。
- `reranker_unavailable`: reranker dependency、model、timeout 或 malformed score 失敗；保留 hybrid candidates 與明確 fallback reason。

## Implementation Guardrails

- `hybrid_rerank` 必須 disabled-by-default，且只能由後續 implementation ticket 明確接入。
- 不得改變 keyword baseline、existing `hybrid` eval behavior、`vector_rerank` fallback behavior 或 Phase 17 trace panel 的缺省顯示。
- 不得引入 BM25 dependency、new score normalization framework 或 production dashboard。
- 若後續 implementation 需要新增 dependency、runtime service、schema 或 API，必須拆成新 ticket 並先回報。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-18-hybrid-rerank-planning/18-01-hybrid-rerank-boundary-contract.md`

## Acceptance Criteria

- [x] `hybrid_rerank` candidate flow 與 disabled-by-default 邊界已寫清楚。
- [x] 已列出必要 trace metadata 與 fallback state，但不新增 runtime 欄位或程式碼。
- [x] Out of Scope 明確排除 backend API、frontend UI、eval dashboard、infra 與 auth / DB。
- [x] Release Impact 明確寫 `Version bump required: no` 並說明原因。

## Validation

- `rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md`
- `git diff --check`
