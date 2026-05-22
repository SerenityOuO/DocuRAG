# 14-02 Retrieval Quality Contract

## Goal

定義後續 rerank / hybrid search 的 retrieval quality contract，讓 implementation ticket 可以沿用 Phase 13 eval runner 的 metrics 與 output shape 做比較。此 ticket 只做 Markdown contract，不新增程式碼。

## Scope

- 定義 planned strategy labels，例如 `keyword`、`vector`、`vector_rerank`、`hybrid`、`hybrid_rerank`。
- 定義 future rerank result trace 欄位，例如 candidate rank、rerank score、rerank latency、fallback reason。
- 定義 hybrid retrieval 的 planned trace 欄位，例如 keyword candidates、vector candidates、merge policy 與 dedupe rule。
- 定義 failure / fallback 行為的文件 contract，確保 optional path 不影響 keyword baseline。
- 定義 Phase 13 metrics 如何延伸比較 rerank / hybrid，但不新增新的 scoring implementation。

## Out of Scope

- 不新增或修改 backend 程式碼。
- 不新增 rerank、hybrid search、BM25、score fusion、model client 或 runtime provider。
- 不新增 LLM-as-judge、answer faithfulness、citation quality scoring 或 eval dashboard。
- 不修改 `sample-data/eval/retrieval-eval.json`。
- 不新增 Redis、NATS、worker、async queue、PostgreSQL schema、登入或 RBAC。
- 不讓任何 future strategy 成為 default-on path。

## Release Impact

- Target version: `v0.14.0`。
- Version bump required: no。
- 原因：本 ticket 只建立 retrieval quality contract 文件，不完成 release，也不改變 runtime 行為。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md`

## Contract Notes

### Planned strategy labels

以下 labels 是 future retrieval quality comparison contract，除已存在的 `keyword` / `vector` 外，其餘皆不代表目前 runtime 已實作：

| Label | Status | Planned meaning |
|---|---|---|
| `keyword` | current baseline | 使用現有 local keyword retrieval，必須維持無外部 runtime 也可執行。 |
| `vector` | optional current path | 使用既有 disabled-by-default embedding + Qdrant retrieval，失敗時 fallback。 |
| `vector_rerank` | future label | 先取 vector candidates，再用 optional reranker 重排 top candidates。 |
| `hybrid` | future label | 合併 keyword candidates 與 vector candidates，套用文件化 merge / dedupe policy。 |
| `hybrid_rerank` | future label | 先產生 hybrid candidates，再用 optional reranker 重排。 |

Future implementation 不得讓 `vector_rerank`、`hybrid` 或 `hybrid_rerank` 成為 default-on path；啟用條件必須由後續 ticket 明確定義。

### Rerank trace metadata contract

Future rerank result 應能在 trace metadata 記錄下列欄位，讓 Phase 13 eval runner 可比較 rerank 前後行為：

- `strategy_label`：例如 `vector_rerank` 或 `hybrid_rerank`。
- `rerank_enabled`：是否實際執行 rerank。
- `rerank_provider` / `rerank_model`：實際 provider 與 model；未啟用時可為 `null`。
- `input_candidate_count`：送入 reranker 前的候選 chunk 數量。
- `rerank_top_k`：rerank 後保留的候選數。
- `rerank_latency_ms`：rerank 階段耗時。
- `fallback_reason`：reranker 未啟用、不可用、timeout、model missing、response malformed 或其他 fallback 原因。
- `candidates`：每個候選 chunk 的 `chunk_id`、`document_id`、原始 rank、原始 score、rerank rank、rerank score 與 source label。

Trace 欄位只作 contract，不要求本 ticket 新增 schema、API response 或 frontend UI。

### Hybrid retrieval trace metadata contract

Future hybrid retrieval 應先文件化以下欄位，再進 implementation：

- `keyword_candidate_count`：keyword branch 產生的候選數。
- `vector_candidate_count`：vector branch 產生的候選數。
- `merge_policy`：候選合併規則，例如 score normalization、rank fusion 或 interleave；實際政策需由後續 ticket 決定。
- `dedupe_rule`：建議以 `document_id` + `chunk_id` 作為去重 key，保留較高 merged rank 的候選。
- `merged_candidate_count`：dedupe 後候選數。
- `branch_failures`：keyword / vector 任一 branch 失敗時的 fallback reason。
- `candidates`：每個候選 chunk 的 source branches、branch ranks、branch scores、merged rank 與 merged score。

Hybrid contract 必須保留 keyword baseline 安全邊界；vector branch 不可用時，future hybrid path 應能退回 keyword-only result。

### Failure and fallback contract

- Reranker disabled：回傳原 retrieval candidates，記錄 `fallback_reason=reranker_disabled`。
- Reranker unavailable / timeout / malformed response：回傳 rerank 前 candidates，保留原 citations 與 retrieved chunks。
- Vector branch unavailable：future hybrid path 退回 keyword-only candidates，並記錄 vector failure。
- Keyword branch 應維持 baseline，不因 future optional strategy 失敗而不可用。
- Eval runner comparison 仍使用 Phase 13 已定義的 Hit Rate@K、MRR@K、Recall@K、latency 與 failure count；本 ticket 不新增 scoring implementation。

## Acceptance Criteria

- [x] Planned strategy labels 已定義，且清楚標示哪些只是 future labels。
- [x] Rerank trace metadata contract 已記錄。
- [x] Hybrid retrieval trace metadata contract 已記錄。
- [x] Failure / fallback contract 已記錄，並保留 keyword baseline 安全邊界。
- [x] 明確標示此 ticket 不新增 implementation 或 version bump。

## Validation

- `rg -n "vector_rerank|hybrid_rerank|rerank score|fallback|default-on" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md`
- `git diff --check`
