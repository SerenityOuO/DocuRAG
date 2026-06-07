# Multipage OCR Status and Retry

## Goal

將 PDF page images 接到多頁 OCR pipeline，支援 page-level status、retry 與 clear failure handling。

## Scope

- 對每個 page image 執行 provider-selected OCR，保存 OCR text、blocks、confidence 與 timing metadata。
- 將 page-level OCR results 合併為 document chunks，保留 page number 與 source metadata。
- 加入 retry / failure reason handling，並更新 frontend 或 API status 顯示。
- 補 backend tests / smoke，驗證 scanned PDF OCR path。

## Out of Scope

- 不做 full table reconstruction、form understanding、layout analysis 或人工修正版本紀錄。
- 不改 VLM parser provider、RAG ranking、rerank algorithm 或 Agent planner。
- 不新增 production autoscaling 或 GPU scheduling。

## Release Impact

- Target version: `v0.34.0`
- Version bump required: no
- 原因：這是 Phase 34 runtime ticket，版本同步留到 `34-04`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `frontend/src/`
- `scripts/`
- `docs/api.md`
- `TODO.md`
- `tasks/phase-34-production-ocr-scanned-pdf/34-03-multipage-ocr-status-and-retry.md`

## Acceptance Criteria

- [x] Scanned PDF 每頁都有 OCR status、text、blocks 與 failure reason。
- [x] 成功 OCR 的 pages 可產生 page-aware chunks，並可被 RAG / parser 使用。
- [x] Retry 行為明確，不會重複污染 chunks 或 metadata。
- [x] Frontend / API 能清楚呈現 multi-page OCR progress 或結果。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Scanned PDF OCR smoke script。
- `rg -n "multipage|page-level|OCR blocks|retry|scanned PDF" backend frontend scripts docs TODO.md tasks/phase-34-production-ocr-scanned-pdf`
- `git diff --check`

## Validation Result

- `backend\.venv\Scripts\python.exe -m pytest tests/test_document_schemas.py tests/test_documents.py -q`：`66 passed`，1 pytest cache warning。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`：`232 passed`，1 pytest cache warning。
- `npm.cmd run build`：通過。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\scanned-pdf-ocr-smoke.ps1`：`3 passed`，46 deselected，1 pytest cache warning。
- `rg -n "multipage|page-level|OCR blocks|retry|scanned PDF" backend frontend scripts docs TODO.md tasks/phase-34-production-ocr-scanned-pdf`：通過。
- `git diff --check`：通過。
