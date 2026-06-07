# RAG Quality Regression Contract

## Goal

定義 Phase 41 RAG quality regression / DatasetOps 的邊界，讓後續能長期追蹤 RAG 品質，而不是只做單次 demo benchmark。

## Scope

- 定義 golden dataset、eval run、strategy snapshot 與 regression report 的資料邊界。
- 固定 regression metrics：Hit Rate@K、MRR@K、Recall@K、latency、fallback count、failure count 與 trace metadata coverage。
- 定義哪些策略需要比較：keyword、vector、hybrid、vector_rerank、hybrid_rerank 與未來 chunking variants。
- 補充 regression gate 的 pass / warn / fail 判斷原則。

## Out of Scope

- 不新增 backend runtime、frontend UI、CI workflow、資料庫 schema、migration 或外部服務。
- 不新增 LLM-as-judge、answer faithfulness、citation quality scoring 或人工標註工具。
- 不更改現有 RAG ranking、chunking 或 `/rag/query` 預設行為。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 41 contract ticket，只定義品質回歸邊界，不改 runtime。

## Files likely to change

- `docs/ROADMAP.md`
- `docs/api.md`
- `docs/architecture.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-41-rag-quality-regression-datasetops/41-01-rag-quality-regression-contract.md`

## Acceptance Criteria

- [ ] 文件定義 Phase 41 golden dataset / regression report / strategy snapshot 的資料邊界。
- [ ] 文件列出 Hit Rate@K、MRR@K、Recall@K、latency、fallback count 與 failure count 的 regression use case。
- [ ] 文件明確說明 Phase 41 不新增 LLM-as-judge 或 production eval dashboard。

## Validation

- `rg -n "Phase 41|RAG quality regression|golden dataset|Hit Rate|MRR|Recall|fallback count|regression gate" docs README_DEV.md TODO.md tasks/phase-41-rag-quality-regression-datasetops`
- `git diff --check`
