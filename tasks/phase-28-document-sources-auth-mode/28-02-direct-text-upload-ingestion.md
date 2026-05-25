# 28-02 Direct Text Upload Ingestion

## Goal

讓 `.txt` 成為正式文件來源：上傳 `.txt` 後，系統直接用原文建立 local chunks，並能接到既有 parser、RAG、Qdrant vector indexing 與 Agent search。這不是 OCR，source 應標示為 `text_upload`。

目前專案雖可上傳 `.txt`，但內容是透過 mock OCR path 包進 OCR text，source 也會變成 `ocr_mock`。Phase 28 要把這條路徑修正成更合理的「文字檔直接進知識庫」。

## Scope

- 新增或整理 backend direct text ingestion flow：讀取 `.txt` UTF-8 內容、做基本空白 normalization、建立 `DocumentChunk`。
- `.txt` 成功 ingestion 後，document processing 應清楚標示 text ingestion / local indexing completed；不得把它說成 OCR completed。
- Chunks 的 `source` / `source_type` / metadata 應使用 `text_upload`，metadata 應保留 `origin=uploaded_text` 或等價資訊。
- `POST /documents/{document_id}/index/vector` 應可索引 `.txt` direct chunks 到 Qdrant，payload 保留 source metadata。
- Deterministic parser 可讀 `.txt` chunks / normalized text 產生 structured fields；VLM image path 對 `.txt` 仍應 clear fallback。
- Agent `search_documents` 可搜尋 `.txt` direct chunks，citation 顯示來源為 text upload。
- Frontend upload flow 遇到 `.txt` 時不要先呼叫 provider-selected OCR；應走 direct text ingestion + best-effort parser / vector indexing。
- 新增 focused tests 覆蓋 `.txt` upload、direct chunks、RAG retrieval、vector indexing preflight / fallback、Agent search。

## Out of Scope

- 不支援 `.docx`、`.xlsx`、HTML、Markdown 或 CSV；本 ticket 只做 `.txt`。
- 不新增 PDF text extraction 或 PDF rendering；留給 `28-03`。
- 不新增 production worker、queue、DB schema、Redis、NATS 或 background ingestion pipeline。
- 不新增正式 Auth / RBAC；login mode 留給 `28-04`。
- 不把 VLM structured fields 自動寫成 retrieval chunks。
- 不改 embedding model、rerank algorithm 或 eval metric 定義。

## Release Impact

- Target version: `v0.28.0`.
- Version bump required: yes when Phase 28 release sync is completed.
- 原因：`.txt` 上傳後的處理方式、chunks source、frontend ingestion flow 與 RAG / Agent evidence 都會變成使用者可見行為。

## Files likely to change

- `backend/app/services/document_storage.py`
- `backend/app/api/routes/documents.py`
- `backend/app/schemas/documents.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_rag.py`
- `backend/tests/test_agent.py`
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

- [x] 上傳 `.txt` 後，系統可直接建立 local chunks，且 chunk `source_type=text_upload`。
- [x] `.txt` direct ingestion 不呼叫 provider-selected OCR，也不使用 `ocr_mock` 當正式來源。
- [x] `.txt` 文件可被 `/rag/query` 搜尋並回傳 citation。
- [x] `.txt` 文件可被 `POST /documents/{document_id}/index/vector` 索引；Qdrant 不可用時仍有清楚 fallback。
- [x] Agent `search_documents` 可命中 `.txt` chunks，trace 可看出來源是 text upload。
- [x] Frontend 對 `.txt` 顯示「直接文字匯入」或等價狀態，不顯示成 OCR 成功。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `rg -n "text_upload|uploaded_text|direct text|Direct Text|ocr_mock|source_type" backend/app backend/tests frontend/src README.md backend/README.md frontend/README.md docs/api.md docs/architecture.md docs/demo-script.md TODO.md docs/ROADMAP.md tasks/phase-28-document-sources-auth-mode`
- `git diff --check`

Validation result：

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` passed: `170 passed`（僅 pytest cache 權限警告）。
- `npm.cmd run build` passed.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` passed；第一次使用 repo root `.tmp` data dir 時因本機權限無法建立測試資料夾，改用 `backend/.tmp/phase28-smoke-data` 後通過。
- Ticket `rg` passed.
- `git diff --check` passed（僅 Windows LF/CRLF 提示）。
