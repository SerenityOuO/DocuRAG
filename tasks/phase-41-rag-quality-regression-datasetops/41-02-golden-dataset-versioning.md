# Golden Dataset Versioning

## Goal

建立可版本化的 RAG golden dataset 管理方式，讓 eval cases 可以追蹤來源、版本、預期答案與適用策略。

## Scope

- 新增或整理 `sample-data/eval/` 下的 golden dataset metadata。
- 定義 eval case version、source document version、expected evidence、expected answer outline 與 case tags。
- 補充 dataset changelog，讓後續新增 case 可說明原因。
- 保留 demo-safe synthetic data 邊界，不放真實個資或公司敏感資料。

## Out of Scope

- 不新增資料庫 schema、dataset upload API、frontend dataset editor 或 production labeling workflow。
- 不新增外部標註工具或人工審核系統。
- 不修改 retrieval eval runner 的策略計算邏輯，除非 ticket 內只需讀取新增 metadata。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 41 dataset artifact ticket，版本同步留到 `41-05`。

## Files likely to change

- `sample-data/eval/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-41-rag-quality-regression-datasetops/41-02-golden-dataset-versioning.md`

## Acceptance Criteria

- [ ] Golden dataset metadata 可描述 case version、source document version、expected evidence 與 case tags。
- [ ] Dataset changelog 說明新增或調整 eval cases 的理由。
- [ ] 文件清楚標示資料為 demo-safe synthetic data。

## Validation

- `rg -n "golden dataset|case version|source document version|expected evidence|dataset changelog|demo-safe" sample-data docs README_DEV.md TODO.md tasks/phase-41-rag-quality-regression-datasetops`
- `git diff --check`
