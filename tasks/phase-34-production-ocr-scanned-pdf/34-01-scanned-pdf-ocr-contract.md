# Scanned PDF OCR Contract

## Goal

定義 Phase 34 scanned PDF / production OCR pipeline 的 contract，補上目前 text-native PDF 與 image OCR 之間的明確缺口。

## Scope

- 定義 PDF source routing：text-native PDF、scanned PDF、mixed PDF、invalid PDF。
- 定義 page image、OCR block、page-level status、retry 與 failure reason contract。
- 定義 OCR result 如何接 parser、chunks、vector indexing 與 worker status。
- 更新 docs / TODO / ROADMAP 的 Phase 34 邊界。

## Out of Scope

- 不新增 PDF rendering runtime 或 OCR code。
- 不做完整 table reconstruction、layout analysis、human correction workflow 或 production accuracy tuning。
- 不修改 VLM parser、RAG ranking、Agent planner 或 eval dashboard。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 34 contract ticket，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-34-production-ocr-scanned-pdf/34-01-scanned-pdf-ocr-contract.md`

## Acceptance Criteria

- [x] 文件明確定義 scanned PDF 與 text-native PDF 的分流規則。
- [x] Page-level OCR status、retry、failure reason 與 OCR blocks contract 完整。
- [x] 文件說明 OCR results 如何接 parser / indexing worker，但不提前實作。
- [x] 明確標示本 ticket 不等於 production OCR runtime。

## Validation

- `rg -n "scanned PDF|pdf_text|page image|OCR block|page-level|Phase 34" docs README_DEV.md TODO.md tasks/phase-34-production-ocr-scanned-pdf`
- `git diff --check`

## Validation Result

- Passed: `rg -n "scanned PDF|pdf_text|page image|OCR block|page-level|Phase 34" docs README_DEV.md TODO.md tasks/phase-34-production-ocr-scanned-pdf`。
- Passed: `git diff --check`（僅 Windows LF/CRLF 提示）。
