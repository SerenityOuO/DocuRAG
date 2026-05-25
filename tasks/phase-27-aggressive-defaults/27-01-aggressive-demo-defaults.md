# 27-01 Aggressive Demo Defaults

## Goal

將已完成、可驗證、且已有 fallback 的進階 demo 能力改成預設路徑：VLM-first parser 維持預設，RAG 查詢預設改走 `hybrid_rerank`，frontend 後台 ingestion 在 OCR 後預設 best-effort 執行 parser 與 vector indexing。這是 aggressive demo default，不是 production runtime 擴張。

## Scope

- 將 backend 預設版本同步到 `v0.27.0`。
- 將 RAG retrieval 預設由 keyword 改為 `hybrid_rerank`，embedding 預設使用 Ollama，rerank 預設使用 FastEmbed adapter。
- 將 `vector_rerank`、`hybrid` 與 `hybrid_rerank` runtime provider 接到 `/rag/query` 與 Agent `search_documents` 使用的 RAG provider。
- frontend 預設打開 Admin / Analyst ingestion surface，並在 OCR 成功後 best-effort 呼叫 VLM-first parser 與 Qdrant vector indexing。
- 更新 demo smoke、Docker Compose env、README、backend README、frontend README、demo script、API / architecture / roadmap / TODO。
- 新增或更新 focused tests，驗證 aggressive default provider selection、hybrid rerank fallback 與版本同步。

## Out of Scope

- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、project permission 或 multi-user isolation。
- 不新增 OpenAI SDK、vLLM serving、streaming、function calling、production VLM parser、PDF rendering、多頁 parser pipeline 或 production eval dashboard。
- 不讓 Agent 執行任意 SQL、delete、reindex、shell command、file system command 或 destructive tools。
- 不新增額外外部依賴；Ollama、Qdrant 與 FastEmbed adapter 只使用既有 lazy import 與 fallback behavior。
- 不新增或 push tag，不建立正式 release。

## Release Impact

- Target version: `v0.27.0`。
- Version bump required: yes。
- 原因：本 ticket 改變 `/rag/query`、Agent search 與 frontend ingestion 的使用者可見預設行為，需形成明確 release 紀錄。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/api/routes/rag.py`
- `backend/app/services/rag.py`
- `backend/tests/test_rag.py`
- `backend/tests/test_health.py`
- `backend/pyproject.toml`
- `frontend/src/App.vue`
- `frontend/src/api/client.ts`
- `frontend/package.json`
- `frontend/package-lock.json`
- `scripts/demo-smoke-test.ps1`
- `infra/docker-compose.yml`
- `.env.example`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.27.0`。
- [x] 未覆寫 env 時，backend RAG provider 預設為 `hybrid_rerank`，embedding provider 為 Ollama，rerank provider 為 FastEmbed adapter。
- [x] `/rag/query` 支援 `vector`、`vector_rerank`、`hybrid` 與 `hybrid_rerank` provider；當 embedding、Qdrant 或 reranker 不可用時，回到 keyword evidence，並在 trace 裡清楚說明 fallback。
- [x] frontend 預設進入後台 ingestion surface；OCR 完成後會 best-effort 解析欄位與嘗試 vector indexing，失敗時不阻斷文件可查詢流程。
- [x] Demo smoke baseline 在沒有 Qdrant / FastEmbed runtime 時仍可通過，並接受 aggressive fallback trace。
- [x] 文件明確說明本次打開的是已完成的 advanced demo defaults，不代表 production DB、worker、auth、vLLM 或 OpenAI API 已完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Browser check for local frontend default Admin / Analyst ingestion surface, retrieval source / fallback display, and no obvious horizontal overflow.
- `rg -n "v0.27.0|Phase 27|aggressive|hybrid_rerank|DOCURAG_RAG_RETRIEVAL_PROVIDER|DOCURAG_EMBEDDING_PROVIDER|DOCURAG_RERANK_PROVIDER" README.md backend/README.md frontend/README.md docs/demo-script.md docs/ROADMAP.md docs/api.md docs/architecture.md TODO.md backend/app frontend/src scripts infra tasks/phase-27-aggressive-defaults`
- `git diff --check`

Validation result：

- Backend tests passed: `166 passed`（僅 pytest cache 權限警告）。
- Frontend build passed.
- Demo smoke passed: health version `0.27.0`，retrieval source `hybrid_rerank fallback: reranker_unavailable`。
- Browser check passed: desktop 1280px 與 mobile 390px 預設皆為後台 ingestion surface，且無 horizontal overflow。
- Ticket `rg` 與 `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
