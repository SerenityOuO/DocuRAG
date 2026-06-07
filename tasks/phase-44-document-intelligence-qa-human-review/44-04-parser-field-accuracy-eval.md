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

- [ ] Parser field accuracy eval 可輸出 field accuracy、missing field、wrong value 與 evidence mismatch。
- [ ] Report 包含 parser_source、fallback reason、confidence bucket 與 sample count。
- [ ] 文件清楚說明 parser eval 不等於 RAG retrieval eval。

## Validation

- Parser field accuracy smoke。
- Backend tests if runtime changes。
- `rg -n "parser field accuracy|missing field|wrong value|evidence mismatch|confidence bucket|parser_source" backend scripts sample-data docs README_DEV.md TODO.md tasks/phase-44-document-intelligence-qa-human-review`
- `git diff --check`
