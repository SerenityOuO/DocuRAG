# 12-02 Vector Indexing Service

## Goal

新增最小同步 vector indexing service/helper，讓已完成 OCR 且已有 chunks 的 documents 可以被明確 index 到 Qdrant，而不是只在 `/rag/query` request path 臨時 embed + upsert。

## Scope

- 新增 backend vector indexing service/helper。
- 將 document chunks embed 後 idempotently upsert 到 `docurag_chunks_v1`。
- Point id 使用穩定規則，例如以 chunk id 生成 deterministic UUID。
- Payload 保留 `document_id`、`filename`、`chunk_id`、`text`、`source`、`source_type`、`page_number`、`bbox`、`confidence`、`created_at` 與 chunk metadata。
- Indexing success / failure 需有明確 result object，供後續 API ticket 使用。
- Embedding unavailable、Qdrant unavailable、collection missing、dimension mismatch、empty chunks 時，回傳清楚錯誤，不破壞 local metadata 或 keyword RAG baseline。
- 單元測試覆蓋 success、idempotent point id、empty chunks、embedding failure、Qdrant failure、collection mismatch。

## Out of Scope

- 不新增 API endpoint。
- 不新增 frontend UI。
- 不新增 background worker、Redis、NATS 或 async queue。
- 不新增 PostgreSQL schema 或 migration。
- 不改 `/rag/query` 預設 keyword baseline。
- 不實作 rerank、hybrid search 或 eval runner。
- 不新增 VLM parser、PDF rendering 或 production OCR pipeline。

## Release Impact

- Target version: `v0.12.0`。
- Version bump required: no。
- 原因：此 ticket 只新增 service building block，不完成 Phase 12 release；版本同步留到 `12-04`。

## Files likely to change

- `backend/app/services/rag.py`
- `backend/app/services/vector_store.py`
- `backend/app/services/embedding.py`
- `backend/app/services/vector_indexing.py`
- `backend/tests/test_vector_indexing.py`
- `TODO.md`

## Acceptance Criteria

- [ ] 有可由 API 或 smoke script 重用的 vector indexing service/helper。
- [ ] Indexing 成功時會 upsert stable point ids 與完整 chunk payload。
- [ ] Empty chunks 不會造成 crash，會回傳明確 skipped result。
- [ ] Embedding / Qdrant / collection failure 不會破壞 keyword RAG baseline。
- [ ] 單元測試覆蓋主要 success 與 failure path。
- [ ] 不改 `/rag/query` 預設行為。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `git diff --check`
