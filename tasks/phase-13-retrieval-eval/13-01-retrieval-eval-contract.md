# 13-01 Retrieval Evaluation Contract

## Goal

固定 Phase 13 / `v0.13.0` 的 retrieval evaluation baseline contract，讓後續 implementation ticket 可以用同一份公開 demo dataset 與 metrics 比較 keyword / vector retrieval。此 ticket 只做文件規劃，不新增 runtime。

## Scope

- 定義 Phase 13 的 evaluation 目標、release boundary 與 guardrails。
- 固定 eval dataset schema，例如 `query`、`expected_document_id`、`expected_chunk_ids`、`expected_terms`、`top_k`、`tags`。
- 固定 retrieval metrics：`Hit Rate@K`、`MRR@K`、`Recall@K`、latency 與 failure count。
- 定義 strategy labels：`keyword`、`vector`，以及 optional vector unavailable fallback 的記錄方式。
- 定義 eval result output contract，包含 per-query rows 與 summary metrics。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 13 backlog。

## Out of Scope

- 不新增或修改 backend 程式碼。
- 不新增 eval runner、API endpoint 或 frontend UI。
- 不新增 rerank、hybrid search 或 ranking model。
- 不新增 Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 eval、vector retrieval 或 vector indexing 成為 default-on path。

## Release Impact

- Target version: `v0.13.0`。
- Version bump required: no。
- 原因：本 ticket 只建立 Phase 13 contract 與 backlog，不完成 runtime release；版本同步留到 `13-04`。

## Contract Details

### Phase 13 Boundary

Phase 13 只建立 retrieval evaluation baseline，目標是讓既有 keyword baseline 與 optional vector retrieval 有可重跑、可比較的 metrics。此階段不評估 answer quality，也不引入新的 ranking strategy。

Keyword eval 必須能在沒有 Ollama embedding、Qdrant 或任何 external runtime 時執行。Vector eval 只能在明確 env、Qdrant collection 與 manual vector indexing 完成後執行；若 vector runtime 不可用，runner / smoke 必須回報清楚 preflight 或 fallback 狀態，不可影響 keyword baseline。

### Eval Dataset Schema

Dataset 使用 JSON array，每筆 case 至少包含：

- `id`: stable eval case id，例如 `invoice_total_amount`。
- `query`: 要送入 retrieval 的查詢文字。
- `top_k`: 每筆 case 的 retrieval cutoff，預設可為 `3`。
- `expected_document_filenames`: 期望命中的 sample document filename list；Phase 13 不依賴固定 document id。
- `expected_chunk_hints`: 期望命中 chunk 的文字線索或 stable hint，例如 `invoice_number`、`payment_terms`。
- `expected_terms`: 用來輔助驗證 evidence 的關鍵字 list。
- `tags`: 分類標籤，例如 `invoice`、`contract`、`support`、`zh-tw`。

允許 optional 欄位：

- `notes`: 說明此 case 的來源或預期 evidence。
- `expected_source_types`: 若需要區分 `mock_ocr`、`ocr` 或 future source type，可由 runner 讀取但不強制要求。

### Metrics

- `Hit Rate@K`: 每筆 query 只要 top K 任一 retrieved chunk 命中 expected document 或 expected chunk hint，即計為 hit；summary 為 hit query 數除以 total query 數。
- `MRR@K`: 找出 top K 中第一個 relevant chunk 的 rank，單筆為 `1 / rank`；若無 relevant chunk 則為 `0`，summary 取平均。
- `Recall@K`: 單筆以 top K 命中的 expected evidence 數除以 expected evidence 總數；若只有 document-level expectation，則以 expected document 命中與否計算。
- `latency_ms`: 單筆 query retrieval 評估耗時；summary 至少包含 average latency。
- `failure_count`: runner / retrieval strategy 發生 exception、preflight failure 或回傳格式不可用的 case 數。

### Strategy Labels

- `keyword`: 預設 baseline，使用既有 local keyword retrieval / `/rag/query` path。
- `vector`: optional path，只在明確 env 與 manual vector indexing 後使用 Qdrant retrieval。
- `vector_unavailable_fallback`: optional vector preflight 或 runtime 不可用時的記錄狀態；不得覆蓋 keyword baseline metrics。

Phase 13 不加入 `hybrid`、`rerank`、`llm_judge` 或任何 ranking model label。

### Result Output Contract

Runner output 必須同時支援人可讀 summary 與 machine-readable JSON。JSON 至少包含：

- `run_id`、`created_at`、`strategy`、`top_k`。
- `dataset_path` 與 `case_count`。
- `summary`: `hit_rate_at_k`、`mrr_at_k`、`recall_at_k`、`average_latency_ms`、`failure_count`。
- `results`: per-query rows，每列包含 `case_id`、`query`、`top_k`、`latency_ms`、`hit`、`first_relevant_rank`、`recall_at_k`、`matched_expected_terms`、`retrieved_chunks`、`error`。
- `environment`: 只記錄必要 strategy/env metadata，例如 retrieval provider、embedding provider/model、Qdrant collection；不得記錄 secret。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md`

## Acceptance Criteria

- [x] Phase 13 goal、scope 與 guardrails 已記錄。
- [x] Eval dataset schema 已記錄。
- [x] Retrieval metrics 與 result output contract 已記錄。
- [x] Phase 13 backlog 已加入 `TODO.md` 與 `docs/ROADMAP.md`。
- [x] 明確標示此 ticket 不 bump version。

## Validation

- `rg -n "v0.13.0|phase-13|Retrieval Evaluation|Hit Rate|MRR" TODO.md docs/ROADMAP.md tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md`
- `git diff --check`
