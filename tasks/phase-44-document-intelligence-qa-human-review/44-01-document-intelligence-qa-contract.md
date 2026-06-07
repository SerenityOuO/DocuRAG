# Document Intelligence QA Contract

## Goal

定義 Phase 44 Document Intelligence QA / human review loop 邊界，讓 OCR / VLM parser 結果可被檢查、修正與量化。

## Scope

- 定義 field confidence、evidence source、source page、source bbox、review status 與 correction version 的資料邊界。
- 定義 parser field accuracy、missing field、wrong value、evidence mismatch 等評估指標。
- 定義 human correction 如何形成 golden labels，並回饋 parser / VLM eval。
- 說明 Phase 44 與既有 OCR / VLM evidence alignment 的關係。

## Out of Scope

- 不新增 full annotation platform、production workflow、多人審核權限或外部 labeling tool。
- 不新增 layout analysis、table reconstruction、deskew deep tuning 或 production OCR accuracy tuning。
- 不修改 parser / OCR default behavior。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 44 contract ticket，只定義文件理解 QA 邊界，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-44-document-intelligence-qa-human-review/44-01-document-intelligence-qa-contract.md`

## Acceptance Criteria

- [ ] 文件定義 field confidence、evidence source、review status 與 correction version。
- [ ] 文件列出 parser field accuracy、missing field、wrong value 與 evidence mismatch 指標。
- [ ] 文件明確說明 Phase 44 不新增 full annotation platform。

## Validation

- `rg -n "Phase 44|Document Intelligence QA|field confidence|evidence|human correction|golden labels|field accuracy" docs README_DEV.md TODO.md tasks/phase-44-document-intelligence-qa-human-review`
- `git diff --check`
