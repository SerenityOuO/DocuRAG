# Eval Dashboard Contract

## Goal

定義 Phase 36 RAG eval dashboard / rerank analysis 的產品與資料 contract，從目前 built-in benchmark 升級為可管理的 evaluation surface。

## Scope

- 定義 eval dataset、eval item、eval run、strategy comparison、failure case 與 fallback case 的 API / UI contract。
- 定義 metrics：Hit Rate@K、MRR@K、Recall@K、Precision@K、latency、failure count、fallback count。
- 定義 rerank analysis 欄位：rerank 前後排名、score、final score source、trace metadata coverage。
- 更新 docs、TODO、ROADMAP 與 README_DEV。

## Out of Scope

- 不新增 dashboard runtime、frontend UI 或 eval dataset persistence。
- 不新增 LLM-as-judge、answer faithfulness、citation quality scoring 或 OCR eval。
- 不修改 retrieval ranking algorithm 或 rerank provider。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 36 contract ticket，不改 runtime。

## Files likely to change

- `docs/api.md`
- `docs/architecture.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-36-eval-dashboard-rerank-analysis/36-01-eval-dashboard-contract.md`

## Acceptance Criteria

- [ ] 文件定義 eval dashboard 的 API / UI contract。
- [ ] Metrics contract 包含 Hit Rate、MRR、Recall、Precision、latency 與 fallback / failure counts。
- [ ] Rerank analysis 欄位清楚區分 pre-rerank / post-rerank。
- [ ] 明確標示 LLM-as-judge 與 answer faithfulness 不在本 ticket scope。

## Validation

- `rg -n "eval dashboard|Hit Rate|MRR|Recall|Precision|rerank analysis|Phase 36" docs README_DEV.md TODO.md tasks/phase-36-eval-dashboard-rerank-analysis`
- `git diff --check`
