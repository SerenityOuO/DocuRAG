# Parser Field Accuracy Eval

## Goal

建立 parser field accuracy eval，量化 OCR / VLM / deterministic parser 對結構化欄位的抽取品質。

## Scope

- 讀取 parser result 與 golden labels，比對 exact match / normalized match / missing / wrong value。
- 輸出 field accuracy、document accuracy、missing field count、wrong value count、evidence mismatch count。
- 報告需標示 parser_source、fallback reason、confidence bucket 與 sample count。
- 文件說明此 eval 與 RAG retrieval eval 的差異。

## Out of Scope

- 不新增 LLM-as-judge、不自動修正 parser、不做模型訓練。
- 不新增 production analytics dashboard 或 long-term metric storage。
- 不更改 parser default provider 或 VLM prompt。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 44 parser eval artifact ticket，版本同步留到 `44-05`。

## Files likely to change

- `backend/`
- `scripts/`
- `sample-data/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-44-document-intelligence-qa-human-review/44-04-parser-field-accuracy-eval.md`

## Acceptance Criteria

- [x] Parser field accuracy eval 可輸出 field accuracy、missing field、wrong value 與 evidence mismatch。
- [x] Report 包含 parser_source、fallback reason、confidence bucket 與 sample count。
- [x] 文件清楚說明 parser eval 不等於 RAG retrieval eval。

## Validation

- Parser field accuracy smoke。
- Backend tests if runtime changes。
- `rg -n "parser field accuracy|missing field|wrong value|evidence mismatch|confidence bucket|parser_source" backend scripts sample-data docs README_DEV.md TODO.md tasks/phase-44-document-intelligence-qa-human-review`
- `git diff --check`

## Completion Notes

- 新增 `scripts/parser-field-accuracy-smoke.ps1`，可讀取 golden labels 與 parser result fixture 並輸出 `parser_field_accuracy_report_v1`。
- 新增 `sample-data/eval/parser-field-results.json` 與 `sample-data/eval/parser-field-accuracy-report.json`；tracked report 可用同一支 smoke script 重生。
- Report 目前展示 field accuracy `0.6`、sample count `5`、missing field / wrong value / evidence mismatch 各 `1`，並保留 parser_source、fallback reason 與 confidence bucket。
- Validation 已通過：parser field accuracy smoke、Phase 44 keyword `rg` 與 `git diff --check`。本 ticket 未改 backend runtime，因此未跑 backend tests。
