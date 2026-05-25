# 28-03 Text-Native PDF Ingestion

## Goal

補齊 PDF 上傳的第一個可用版本：支援 text-native PDF 文字抽取並建立 chunks；如果 PDF 是掃描圖，則明確標示為 `pdf_scanned_pending_ocr`，不假裝已完成。

`goal.md` 對 PDF 的長期要求包含 PDF 轉頁面圖片與 OCR，但那是 scanned PDF / 多頁 OCR pipeline。Phase 28 先做比較小、可驗證的 text-native PDF ingestion，讓可複製文字的 PDF 可以進 RAG / Qdrant / Agent。

## Scope

- 選定 text-native PDF extraction provider，優先使用小而清楚的 Python PDF text extraction dependency；新增 dependency 時必須更新 backend docs 與 validation。
- 上傳 PDF 後，先嘗試抽取文字；有文字時建立 chunks，source 使用 `pdf_text`。
- 保留 page number metadata；若 extractor 無法提供 bbox，bbox 應為 `null`，不可假造。
- 若 PDF 沒有可抽文字或 extractor 判斷為空內容，document 應進入 clear pending / unsupported state，例如 `pdf_scanned_pending_ocr`。
- Scanned PDF 不自動送 PaddleOCR，除非後續 ticket 已完成 PDF rendering；錯誤訊息要說明需要 rendering / OCR pipeline。
- Frontend 顯示 PDF ingestion 結果：text-native PDF ready、scanned PDF pending OCR、PDF extraction failed。
- RAG、Qdrant vector indexing、Agent search 可使用 `pdf_text` chunks。
- 新增至少一份 demo-safe text-native PDF sample 或 fixture，覆蓋 PDF extraction test。

## Out of Scope

- 不做 PDF rendering、page image conversion、scanned PDF OCR、多頁 OCR worker、layout analysis 或 table reconstruction。
- 不保證所有 PDF 排版、表格與欄位都能完整還原；本 ticket 只抽文字層。
- 不新增 production worker、queue、DB schema、Redis、NATS、K8s 或 deployment 設定。
- 不新增正式 Auth / RBAC；login mode 留給 `28-04`。
- 不把 PDF text extraction 結果自動當成 VLM structured fields。
- 不修改 OCR provider selection 或 PaddleOCR GPU lifecycle。

## Release Impact

- Target version: `v0.28.0`.
- Version bump required: yes when Phase 28 release sync is completed.
- 原因：PDF 上傳後的可用行為、document processing state、chunks source 與 RAG / Agent evidence 都會改變。

## Files likely to change

- `backend/pyproject.toml`
- `backend/app/services/document_storage.py`
- `backend/app/api/routes/documents.py`
- `backend/app/schemas/documents.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_rag.py`
- `backend/tests/test_agent.py`
- `sample-data/documents/`
- `frontend/src/App.vue`
- `frontend/src/api/client.ts`
- `scripts/demo-smoke-test.ps1`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [ ] Text-native PDF 上傳後可抽出文字並建立 chunks，chunk `source_type=pdf_text`。
- [ ] PDF chunks 保留 page number metadata；沒有 bbox 時明確為 `null`。
- [ ] Scanned / empty PDF 不被標示為 ready，狀態或 trace 需顯示 `pdf_scanned_pending_ocr` 或等價原因。
- [ ] PDF text chunks 可被 `/rag/query` 搜尋並回傳 citation。
- [ ] PDF text chunks 可被 Qdrant vector indexing 使用；Qdrant 不可用時 fallback 清楚。
- [ ] Agent `search_documents` 可命中 PDF text chunks。
- [ ] 文件明確說明 Phase 28 支援的是 text-native PDF，不是 scanned PDF OCR。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `rg -n "pdf_text|pdf_scanned_pending_ocr|text-native PDF|PDF text|scanned PDF|source_type" backend/app backend/tests frontend/src README.md backend/README.md frontend/README.md docs/api.md docs/architecture.md docs/demo-script.md TODO.md docs/ROADMAP.md tasks/phase-28-document-sources-auth-mode`
- `git diff --check`
