# v0.7.0 OCR Output Normalization

## Goal

把 real OCR provider 的原始輸出收斂到 v0.6 chunk / citation trace contract，讓 page、bbox、confidence 與 metadata 有穩定 default，不讓後續 RAG / citation work 直接依賴 provider 私有格式。

## Scope

- 定義 real OCR output 到 `DocumentChunk` 欄位的 mapping。
- 若 provider 有 page / bbox / confidence，映射到既有 optional 欄位。
- 若 provider 沒有 page / bbox / confidence，使用明確 default 並保留 API 相容。
- 更新 RAG response 中 citations / retrieved_chunks 的 trace metadata。
- 新增 schema 與 metadata persistence 測試。
- 更新 frontend 顯示，避免 optional 欄位缺失時畫面破版。

## Out of Scope

- 不實作 citation evaluation。
- 不接 embedding、Qdrant、rerank、LLM 或 vector indexing。
- 不做 OCR model quality tuning。
- 不新增 PDF rendering pipeline。
- 不新增 queue、worker、Redis、NATS、PostgreSQL、登入或 RBAC。

## Files likely to change

- `backend/app/schemas/documents.py`
- `backend/app/schemas/rag.py`
- `backend/app/services/document_storage.py`
- `backend/app/services/ocr.py`
- `backend/app/services/rag.py`
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

- [ ] real OCR output 可以穩定映射到 `DocumentChunk` trace 欄位。
- [ ] 缺少 page / bbox / confidence 時 API response 仍相容。
- [ ] citations 與 retrieved_chunks 都帶出一致 trace metadata。
- [ ] frontend 可顯示 optional trace metadata，缺值時不破版。
- [ ] 測試覆蓋 provider 有 metadata 與缺 metadata 的兩種情境。
- [ ] 沒有新增 embedding、Qdrant、rerank、LLM、queue 或 DB。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`
