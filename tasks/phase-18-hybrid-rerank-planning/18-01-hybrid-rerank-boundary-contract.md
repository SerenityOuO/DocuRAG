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
- 原因：本 ticket 只建立 Phase 18 邊界 contract 與 guardrails，不產生 runtime release artifact；若後續 implementation 形成 release，才由 release sync ticket bump 到 `v0.18.0`。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-18-hybrid-rerank-planning/18-01-hybrid-rerank-boundary-contract.md`

## Acceptance Criteria

- [ ] `hybrid_rerank` candidate flow 與 disabled-by-default 邊界已寫清楚。
- [ ] 已列出必要 trace metadata 與 fallback state，但不新增 runtime 欄位或程式碼。
- [ ] Out of Scope 明確排除 backend API、frontend UI、eval dashboard、infra 與 auth / DB。
- [ ] Release Impact 明確寫 `Version bump required: no` 並說明原因。

## Validation

- `rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md`
- `git diff --check`
