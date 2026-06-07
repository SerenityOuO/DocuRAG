# PDF Rendering Page Image Pipeline

## Goal

新增 demo-safe PDF rendering pipeline，將 scanned PDF 或 mixed PDF 轉成 page images，供後續多頁 OCR worker 使用。

## Scope

- 選定 PDF rendering dependency / approach，並記錄 Windows local validation。
- 將 PDF pages render 成受控尺寸的 page images，保存 metadata。
- 區分 text-native PDF、scanned PDF 與 invalid PDF。
- 補 backend tests 或 smoke，驗證 page image pipeline 與 failure handling。

## Out of Scope

- 不執行 OCR；OCR worker 留給 `34-03`。
- 不做 layout analysis、table reconstruction、deskew tuning 或 image enhancement 深度調參。
- 不新增 production storage service、S3、K8s 或 autoscaling。

## Release Impact

- Target version: `v0.34.0`
- Version bump required: no
- 原因：這是 Phase 34 runtime ticket，版本同步留到 `34-04`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `scripts/`
- `.env.example`
- `docs/architecture.md`
- `TODO.md`
- `tasks/phase-34-production-ocr-scanned-pdf/34-02-pdf-rendering-page-image-pipeline.md`

## Acceptance Criteria

- [x] Scanned PDF 可產生 page images 與 page metadata。
- [x] Text-native PDF 仍走既有 `pdf_text` path，不被錯誤送入 scanned pipeline。
- [x] Invalid / unsupported PDF 有明確 failure reason。
- [x] Validation 覆蓋 page rendering success 與 failure path。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- PDF rendering smoke script 或 targeted tests。
- `rg -n "PDF rendering|page image|scanned|pdf_text|failure reason" backend scripts docs TODO.md tasks/phase-34-production-ocr-scanned-pdf`
- `git diff --check`

## Validation Result

- Targeted tests passed: `backend/.venv/Scripts/python.exe -m pytest tests/test_document_schemas.py tests/test_documents.py -q`（`63 passed`，1 pytest cache warning）。
- Full backend validation passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`229 passed`，1 pytest cache warning）。
- Passed: `rg -n "PDF rendering|page image|scanned|pdf_text|failure reason" backend scripts docs TODO.md tasks/phase-34-production-ocr-scanned-pdf`。
- Passed: `git diff --check`。
