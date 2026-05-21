# v0.6.0 Chunk and Citation Schema Bridge

## Goal

補強 chunk 與 citation metadata contract，讓後續真正 OCR / VLM parser、embedding retrieval 與 citation trace 可以保存頁碼、座標、confidence 與來源資訊，同時保持目前 local RAG demo 可用。

## Scope

- 檢視目前 `DocumentChunk`、`RetrievedChunk` 與 `RagCitation` schema。
- 為 chunk 增加可選 metadata 欄位，例如 `page_number`、`bbox`、`confidence`、`source_type` 或 `metadata`。
- 為 citation 增加可選 trace 欄位，讓未來可以指向 page / chunk / OCR block。
- 保留既有 `chunk_id`、`document_id`、`text`、`source`、`created_at` 欄位。
- 保留 v0.5.1 API response 相容性，新增欄位須有 default 或可選值。
- frontend 顯示 retrieved chunks / citations 時可容忍新增欄位。
- 補上 schema validation、metadata persistence 與 RAG response 測試。
- 更新 README、backend README、frontend README、TODO 與 ROADMAP。

## Out of Scope

- 不做真正 OCR bbox 偵測。
- 不做 PDF page rendering。
- 不做表格、版面或章節切分。
- 不做 embedding、Qdrant、rerank 或 LLM。
- 不做 citation evaluation 指標。
- 不做 database migration。
- 不做登入、RBAC 或權限。

## Files likely to change

- `backend/app/schemas/documents.py`
- `backend/app/schemas/rag.py`
- `backend/app/services/document_storage.py`
- `backend/tests/test_document_schemas.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_rag.py`
- `frontend/src/api/client.ts`
- `frontend/src/App.vue`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] chunk schema 可保存 optional page / bbox / confidence / source metadata。
- [ ] citation schema 可保存 optional trace metadata。
- [ ] 既有 v0.5.1 chunk 與 citation response 欄位仍存在。
- [ ] 舊 metadata 沒有新增欄位時仍能讀取。
- [ ] mock OCR 產生的 chunks 使用合理 default metadata。
- [ ] RAG response 仍包含 deterministic answer、citations 與 retrieved chunks。
- [ ] 測試覆蓋 schema validation、metadata persistence 與 response 相容性。
- [ ] 文件明確說明新增欄位只是 contract，尚未來自真正 OCR / VLM parser。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`
