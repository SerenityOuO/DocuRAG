# v0.6.0 RAG Provider Interface Bridge

## Goal

把目前的 local keyword RAG baseline 整理成可替換的 RAG provider 邊界，讓後續接 embedding、Qdrant、rerank 或 LLM generation 時，可以沿用既有 `/rag/query` contract、citations 與 frontend chat UI。

## Scope

- 建立最小 RAG provider / service 邊界，先只保留 `keyword` provider。
- 將 chunk search、score 計算與 deterministic answer 組裝從 storage / route 中整理到 RAG provider / service 邊界。
- 保留既有 `POST /rag/query` request / response contract。
- 保留 `answer`、`citations`、`retrieved_chunks` 欄位與 frontend 顯示。
- 保留 local JSON metadata store，不新增 DB 或 vector store。
- 補上 keyword provider、empty result、top_k validation 與 citations 的測試。
- 更新 README、backend README、frontend README、TODO 與 ROADMAP，說明目前仍是 keyword provider。

## Out of Scope

- 不做 embedding。
- 不接 Qdrant、FAISS、Chroma 或任何 vector database。
- 不做 rerank。
- 不接真正 LLM、OpenAI API、Ollama 或 vLLM。
- 不做 streaming response。
- 不做 Agent tool calling。
- 不做 Redis、NATS、PostgreSQL、登入或 RBAC。
- 不改 OCR provider。
- 不建立多層抽象或 plugin registry；只做目前會用到的最小 provider 邊界。

## Files likely to change

- `backend/app/services/document_storage.py`
- `backend/app/services/rag.py`
- `backend/app/api/routes/rag.py`
- `backend/app/schemas/rag.py`
- `backend/app/core/config.py`
- `backend/tests/test_rag.py`
- `backend/tests/test_document_schemas.py`
- `frontend/src/api/client.ts`
- `frontend/src/App.vue`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] keyword retrieval 與 deterministic answer 組裝已移入明確的 RAG provider / service 邊界。
- [ ] `POST /rag/query` request / response 與 v0.5.1 相容。
- [ ] empty result 仍回傳 deterministic no-result answer、空 citations 與空 retrieved chunks。
- [ ] citations 仍包含 `document_id`、`filename` 與 `chunk_id`。
- [ ] retrieved chunks 仍包含 score 並依分數排序。
- [ ] frontend chat UI 不需要知道 provider 實作細節。
- [ ] 測試覆蓋 keyword provider、top_k、citations 與 empty result。
- [ ] 文件明確說明目前只有 local keyword provider，尚未接 embedding、Qdrant、rerank 或 LLM。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`
