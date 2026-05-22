# 16-01 Hybrid Retrieval Contract

## Goal

固定 Phase 16 optional `hybrid` retrieval 的 strategy label、candidate merge / dedupe policy 與 trace metadata contract，讓後續 implementation 不需要重新猜測邊界。此 ticket 是文件 ticket，只做 Markdown planning，不改 runtime。

## Scope

- 定義 Phase 16 第一版 `hybrid` strategy：keyword branch + optional vector branch，最後輸出單一 ranked candidate list。
- 規劃 candidate identity 與 dedupe key，優先使用 `(document_id, chunk_id)`，缺少欄位時必須保留清楚 fallback metadata。
- 規劃 merge policy，第一版優先使用 deterministic rank-based fusion，避免引入 BM25 dependency 或 score normalization 風險。
- 定義 trace metadata，例如 branch candidate count、merge policy、dedupe count、branch failure、final rank 與 fallback reason。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 16 hybrid retrieval planning 說明。

## Hybrid Contract

Phase 16 第一版 strategy label 固定為 `hybrid`。此 label 只代表 retrieval eval runner 的 optional strategy，不代表 `/rag/query` 或 frontend UI 已支援 hybrid。

Candidate sources：

- `keyword` branch：沿用現有 keyword baseline candidate list，可在沒有 Ollama embedding、Qdrant 或 FastEmbed runtime 時單獨執行。
- `vector` branch：沿用現有 optional vector retrieval branch，只有在 explicit vector env、Qdrant collection 與 manual vector indexing 已準備好時才參與。
- `vector_rerank` branch 不屬於 `hybrid` 第一版 candidate source；`hybrid_rerank` 留到後續 Phase。

Candidate identity：

- Preferred dedupe key：`(document_id, chunk_id)`。
- 若 `chunk_id` 缺失但 `document_id` 與 `text` 存在，fallback key 可使用 `(document_id, normalized_text)`，並在 trace metadata 記錄 `dedupe_key_fallback="document_text"`。
- 若 candidate 缺少足夠欄位，保留該 candidate 但標記 `dedupe_key_fallback="unavailable"`，不得靜默丟失 citation trace。

Merge policy：

- 第一版固定為 deterministic `rank_based_fusion`。
- 每個 branch 先保留各自排序與 branch rank，再依 rank fusion score 合併；不可用 raw keyword score 與 vector similarity 直接相加。
- 同一 dedupe key 同時出現在 keyword 與 vector branch 時，合併為單一 candidate，保留 `branches=["keyword","vector"]`、各 branch rank 與原始 branch score。
- Tie-breaker 固定使用 `best_branch_rank`、`document_id`、`chunk_id` 的穩定排序，避免 eval result 在同資料下漂移。
- 第一版不新增 BM25 dependency，不做 score normalization，不新增 configurable weights。

Trace metadata：

- Run-level metadata：`strategy_label`、`hybrid_enabled`、`merge_policy`、`dedupe_key`、`keyword_candidate_count`、`vector_candidate_count`、`merged_candidate_count`、`deduped_candidate_count`、`branch_failures`、`fallback_reason`、`latency_ms`。
- Candidate-level metadata：`final_rank`、`merged_score`、`branches`、`keyword_rank`、`keyword_score`、`vector_rank`、`vector_score`、`dedupe_key`、`dedupe_key_fallback`。
- Fallback metadata 必須可讓 eval JSON 看出是完整 hybrid、keyword-only fallback，或 vector branch unavailable。

Fallback behavior：

- Keyword branch 是 baseline；keyword branch 不可因 vector branch 失敗而失效。
- Vector branch disabled、connection error、collection missing、embedding failure 或 empty vector results 時，`hybrid` result fallback 為 keyword-only candidates，strategy trace 記錄 `fallback_reason`。
- 若 keyword branch 有結果但 vector branch 無結果，failure count 仍依 Phase 13 metrics contract 計算，不因 optional branch unavailable 直接視為 eval run failure。
- 若 keyword branch 本身也沒有結果，保留 empty result 與清楚 reason，避免隱性改跑其他 strategy。

## Out of Scope

- 不實作 hybrid retrieval runtime、BM25、score fusion code、merge / dedupe implementation 或 API endpoint。
- 不修改 `backend/`、`frontend/`、`scripts/` 或 `sample-data/eval/retrieval-eval.json`。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 frontend trace UI。
- 不讓 `hybrid`、`vector`、`vector_rerank` 或 rerank provider 成為 default-on path。

## Release Impact

- Target version: `v0.16.0`。
- Version bump required: no。
- 原因：本 ticket 只固定 Phase 16 hybrid retrieval contract，不新增 runtime，也不形成 release artifact；實際版本同步留到 Phase 16 release ticket。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md`

## Acceptance Criteria

- [x] `hybrid` strategy 的 candidate sources、merge policy 與 dedupe key 已文件化。
- [x] Hybrid trace metadata 與 fallback behavior 已文件化。
- [x] 明確標示此 ticket 不修改 runtime、不新增 dependency、不改 dataset JSON。
- [x] `TODO.md` 與 `docs/ROADMAP.md` 已同步 Phase 16 planning 邊界。

## Validation

- `rg -n "v0.16.0|Phase 16|hybrid retrieval|merge policy|dedupe" TODO.md docs/ROADMAP.md tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md`
- `git diff --check`
