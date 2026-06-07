# Qdrant Payload Index and Reindexing

## Goal

強化 Qdrant payload index、metadata filter、reindex document / project 與 stale vector cleanup，提升 RAG indexing quality 與可維護性。

## Scope

- 建立或驗證 Qdrant payload index，支援 tenant / project / document / source filters。
- 新增 reindex document / reindex project 的 backend API 或 script。
- 新增 stale vector cleanup 策略，避免舊 vectors 污染 retrieval。
- 補 backend tests / smoke，驗證 filter、reindex 與 cleanup。

## Out of Scope

- 不新增 production eval dashboard 或 strategy comparison UI。
- 不修改 rerank algorithm、embedding model selection 或 LLM generation。
- 不新增 Redis / NATS worker；若使用 worker 只能接既有 Phase 33 path，不擴張其 scope。

## Release Impact

- Target version: `v0.35.0`
- Version bump required: no
- 原因：這是 Phase 35 runtime ticket，版本同步留到 `35-04`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `scripts/`
- `docs/api.md`
- `docs/architecture.md`
- `TODO.md`
- `tasks/phase-35-rag-indexing-quality/35-03-qdrant-payload-index-and-reindexing.md`

## Acceptance Criteria

- [x] Qdrant payload index / filter 可限制 tenant / project / document scope。
- [x] Reindex document / project 可重新寫入 chunks vectors。
- [x] Stale vector cleanup 有明確 API 或 script，並可被 validation 驗證。
- [x] Runtime unavailable 時保留 fallback / skip 訊息，不破壞 baseline demo。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- Qdrant reindex / cleanup smoke script。
- `rg -n "Qdrant|payload index|reindex|stale vector|tenant|project_id|document_id" backend scripts docs TODO.md tasks/phase-35-rag-indexing-quality`
- `git diff --check`

## Completion Notes

- `QdrantVectorStore` now creates payload indexes for tenant / project / document / source fields and builds filter payloads for tenant, project, document and source scope.
- `VectorIndexingService` now writes `tenant_id`, `project_id`, `content_source` and `chunk_type` into payload metadata, and can run stale point cleanup after successful upsert.
- `POST /documents/{document_id}/index/vector` accepts `cleanup_stale`; `POST /documents/index/vector/reindex` runs project-scope reindex over visible documents.
- `scripts/qdrant-reindex-cleanup-smoke.ps1` validates payload index, reindex and cleanup coverage without requiring a live Qdrant runtime.

## Validation Result

- Focused backend tests: `98 passed` (`tests/test_vector_store.py`, `tests/test_vector_indexing.py`, `tests/test_documents.py`, `tests/test_rag.py`).
- Qdrant reindex / cleanup smoke: `4 passed`.
- Backend full test: `240 passed`.
- Ticket `rg` and `git diff --check` passed with Windows LF/CRLF warnings only.
