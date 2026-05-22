# 14-03 Eval Dataset Expansion Plan

## Goal

規劃 retrieval eval dataset 的擴充方向，讓後續 rerank / hybrid search 可以用更有鑑別度的 case 比較品質。此 ticket 只做文件規劃，不改資料集 JSON。

## Scope

- 定義 Phase 14 dataset expansion 原則，例如公開虛構資料、可重跑、可解釋、避免敏感資訊。
- 規劃要新增的 case 類型，例如 lexical mismatch、multi-evidence、near-duplicate chunks、cross-document ambiguity。
- 定義每種 case 的 expected evidence 描述方式，避免綁死未來 runtime 或資料庫 id。
- 規劃 quality gates，例如 dataset schema validation、minimum case count、tag coverage。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 14 dataset planning 說明。

## Out of Scope

- 不修改 `sample-data/eval/retrieval-eval.json`。
- 不新增 sample documents、PDF、image 或真實業務資料。
- 不新增 backend tests、runner logic、API endpoint 或 frontend UI。
- 不新增 rerank、hybrid search、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不新增外部依賴、Redis、NATS、worker、async queue 或 PostgreSQL schema。

## Release Impact

- Target version: `v0.14.0`。
- Version bump required: no。
- 原因：本 ticket 只規劃 dataset expansion，不新增資料集內容、不改 runtime，也不形成 release artifact。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md`

## Acceptance Criteria

- [ ] Dataset expansion 原則已記錄。
- [ ] 至少四種 future eval case 類型已定義。
- [ ] 每種 case 都說明 expected evidence 設計方式。
- [ ] Quality gates 已記錄，並明確避免敏感資料。
- [ ] 明確標示此 ticket 不修改資料集 JSON。

## Validation

- `rg -n "dataset expansion|lexical mismatch|multi-evidence|near-duplicate|cross-document" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-03-eval-dataset-expansion-plan.md`
- `git diff --check`
