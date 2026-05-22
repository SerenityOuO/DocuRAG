# 16-01 Hybrid Retrieval Contract

## Goal

固定 Phase 16 optional `hybrid` retrieval 的 strategy label、candidate merge / dedupe policy 與 trace metadata contract，讓後續 implementation 不需要重新猜測邊界。此 ticket 是文件 ticket，只做 Markdown planning，不改 runtime。

## Scope

- 定義 Phase 16 第一版 `hybrid` strategy：keyword branch + optional vector branch，最後輸出單一 ranked candidate list。
- 規劃 candidate identity 與 dedupe key，優先使用 `(document_id, chunk_id)`，缺少欄位時必須保留清楚 fallback metadata。
- 規劃 merge policy，第一版優先使用 deterministic rank-based fusion，避免引入 BM25 dependency 或 score normalization 風險。
- 定義 trace metadata，例如 branch candidate count、merge policy、dedupe count、branch failure、final rank 與 fallback reason。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 16 hybrid retrieval planning 說明。

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

- [ ] `hybrid` strategy 的 candidate sources、merge policy 與 dedupe key 已文件化。
- [ ] Hybrid trace metadata 與 fallback behavior 已文件化。
- [ ] 明確標示此 ticket 不修改 runtime、不新增 dependency、不改 dataset JSON。
- [ ] `TODO.md` 與 `docs/ROADMAP.md` 已同步 Phase 16 planning 邊界。

## Validation

- `rg -n "v0.16.0|Phase 16|hybrid retrieval|merge policy|dedupe" TODO.md docs/ROADMAP.md tasks/phase-16-hybrid-retrieval/16-01-hybrid-retrieval-contract.md`
- `git diff --check`
