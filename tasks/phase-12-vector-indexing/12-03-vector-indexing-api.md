# 12-03 Vector Indexing API

## Goal

新增手動 vector indexing API，讓 demo 可以明確執行「document chunks -> embedding -> Qdrant upsert」流程，並把 indexing result 回傳給使用者或 smoke script。

## Scope

- 新增手動 endpoint，例如 `POST /documents/{document_id}/index/vector`。
- Endpoint 只在明確設定 embedding provider 與 Qdrant runtime 可用時嘗試 vector indexing。
- 文件不存在、尚未 OCR、沒有 chunks、embedding failure、Qdrant failure、collection missing / mismatch 都要回傳清楚錯誤或 skipped result。
- 成功 response 包含 document id、indexed chunk count、collection name、embedding provider/model、vector size 與 indexing status。
- 保留 existing keyword RAG baseline 與 optional vector retrieval fallback 行為。
- 更新 API docs / README 中的最小使用說明。
- 單元測試覆蓋 success、document not found、empty chunks、provider disabled、Qdrant failure。

## Out of Scope

- 不新增 frontend UI。
- 不新增 batch indexing。
- 不新增 background worker、Redis、NATS 或 async queue。
- 不新增 PostgreSQL schema 或 migration。
- 不讓 upload / OCR 自動觸發 vector indexing。
- 不改 `/rag/query` 預設 keyword baseline。
- 不實作 rerank、hybrid search 或 eval runner。
- 不新增 VLM parser、PDF rendering 或 production OCR pipeline。

## Release Impact

- Target version: `v0.12.0`。
- Version bump required: no。
- 原因：此 ticket 新增 API building block，但 Phase 12 release / version sync 留到 `12-04`。

## Files likely to change

- `backend/app/api/routes/documents.py`
- `backend/app/services/vector_indexing.py`
- `backend/schemas` 或既有 schema 檔案
- `backend/tests/test_documents.py`
- `docs/api.md`
- `backend/README.md`
- `TODO.md`

## Acceptance Criteria

- [ ] 可對單一 document 手動執行 vector indexing。
- [ ] 成功 response 包含 indexed chunk count 與 Qdrant / embedding metadata。
- [ ] Provider disabled 或 external runtime unavailable 時回傳清楚錯誤，不造成 backend crash。
- [ ] 未完成 OCR 或沒有 chunks 的 document 不會被錯誤 index。
- [ ] 不改 upload、OCR 或 `/rag/query` 預設行為。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `git diff --check`
