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

## Acceptance Criteria

- [ ] Planned strategy labels 已定義，且清楚標示哪些只是 future labels。
- [ ] Rerank trace metadata contract 已記錄。
- [ ] Hybrid retrieval trace metadata contract 已記錄。
- [ ] Failure / fallback contract 已記錄，並保留 keyword baseline 安全邊界。
- [ ] 明確標示此 ticket 不新增 implementation 或 version bump。

## Validation

- `rg -n "vector_rerank|hybrid_rerank|rerank score|fallback|default-on" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-02-retrieval-quality-contract.md`
- `git diff --check`
