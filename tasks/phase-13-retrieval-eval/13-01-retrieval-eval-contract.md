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

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md`

## Acceptance Criteria

- [ ] Phase 13 goal、scope 與 guardrails 已記錄。
- [ ] Eval dataset schema 已記錄。
- [ ] Retrieval metrics 與 result output contract 已記錄。
- [ ] Phase 13 backlog 已加入 `TODO.md` 與 `docs/ROADMAP.md`。
- [ ] 明確標示此 ticket 不 bump version。

## Validation

- `rg -n "v0.13.0|phase-13|Retrieval Evaluation|Hit Rate|MRR" TODO.md docs/ROADMAP.md tasks/phase-13-retrieval-eval/13-01-retrieval-eval-contract.md`
- `git diff --check`
