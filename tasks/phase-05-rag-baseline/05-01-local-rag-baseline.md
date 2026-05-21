# v0.5.0 Local RAG Baseline

## Goal

建立第一版可驗證的本機 RAG baseline，使用 v0.4.0 的 OCR mock text 作為知識來源，提供 chunking、local keyword retrieval、deterministic RAG answer API，以及 frontend 簡易 Chat UI。

## Scope

- 從已完成的 OCR mock text 產生 chunks。
- 每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source`、`created_at`。
- chunks 先保存在 local metadata store，不使用 DB。
- 實作 local keyword retrieval，依 query 從 chunks 找出 `top_k`。
- retrieval 回傳 matched chunks、score、`document_id`、`chunk_id`。
- 新增 `POST /rag/query`。
- request 包含 `query`、`top_k`。
- response 包含 `answer`、`citations`、`retrieved_chunks`。
- answer 先用 deterministic template 產生，不接 LLM。
- citations 指出 `document_id`、`filename`、`chunk_id`。
- frontend 新增簡易問答區，可輸入 query 並顯示 answer、retrieved chunks、citations。
- 保留既有 health、upload、document list、OCR mock UI。
- 更新 README、backend README、frontend README、TODO、ROADMAP 與版本號。

## Out of Scope

- 不接真正 LLM。
- 不接 OpenAI API。
- 不接 Ollama 或 vLLM。
- 不做 embedding。
- 不做 Qdrant。
- 不做 rerank。
- 不做 Redis 或 NATS。
- 不做 PostgreSQL、資料庫 schema 或 migration。
- 不做登入、RBAC 或權限。
- 不改既有 v0.1.0 到 v0.4.0 tags。
- 不做 force push。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/main.py`
- `backend/app/schemas/documents.py`
- `backend/app/schemas/rag.py`
- `backend/app/services/document_storage.py`
- `backend/app/api/routes/rag.py`
- `backend/app/api/routes/__init__.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_document_schemas.py`
- `backend/tests/test_rag.py`
- `backend/pyproject.toml`
- `frontend/src/api/client.ts`
- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `frontend/package.json`
- `frontend/package-lock.json`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `infra/docker-compose.yml`

## Acceptance Criteria

- [x] OCR mock 完成後可從 OCR text 產生並保存 chunks。
- [x] 每個 chunk 包含 `chunk_id`、`document_id`、`text`、`source`、`created_at`。
- [x] local metadata store 保存 chunks，不新增 DB。
- [x] local keyword retrieval 可依 query 回傳 `top_k` matched chunks。
- [x] retrieval result 包含 score、`document_id`、`chunk_id`。
- [x] `POST /rag/query` 接受 `query`、`top_k`。
- [x] `POST /rag/query` 回傳 `answer`、`citations`、`retrieved_chunks`。
- [x] deterministic answer 不接 LLM、OpenAI API、Ollama 或 vLLM。
- [x] citations 包含 `document_id`、`filename`、`chunk_id`。
- [x] frontend 可輸入問題並顯示 RAG answer、retrieved chunks 與 citations。
- [x] 既有 health、upload、document list、OCR mock UI 保留可用。
- [x] backend version 更新為 `0.5.0`。
- [x] frontend package version 更新為 `0.5.0`。
- [x] backend pytest 通過。
- [x] frontend build 通過。
- [x] Docker build 通過。
- [x] Docker Compose 啟動後 `/health`、upload、OCR mock 與 RAG API 都可驗證。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `curl http://127.0.0.1:8000/health`
- `curl -X POST http://127.0.0.1:8000/documents/upload -F "file=@sample.txt"`
- `curl -X POST http://127.0.0.1:8000/documents/{document_id}/ocr/mock`
- `curl http://127.0.0.1:8000/documents/{document_id}/ocr`
- `curl -X POST http://127.0.0.1:8000/rag/query -H "Content-Type: application/json" -d "{\"query\":\"invoice\",\"top_k\":3}"`
- `docker compose -f infra/docker-compose.yml down`
