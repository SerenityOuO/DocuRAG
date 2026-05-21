# v0.6.0 Processing Job Contract Bridge

## Goal

建立最小 processing job contract，讓後續真正 OCR、embedding indexing 或長任務可以被追蹤狀態；本 ticket 只做本機同步流程的 job metadata，不引入真正 queue 或 worker。

## Scope

- 定義 processing job schema，至少包含 `job_id`、`document_id`、`job_type`、`status`、`created_at`、`updated_at` 與可選 `error_message`。
- 先支援 mock OCR / local indexing 這類本機同步 job metadata。
- 可在 local JSON metadata store 中保存 job history 或 latest job summary。
- API response 或 document detail 可讀到與文件相關的 processing job 狀態。
- frontend 可顯示簡單 processing job 狀態，但不需要新建複雜 job dashboard。
- 補上 job schema、metadata persistence 與既有 demo flow 相容性測試。
- 更新 README、backend README、frontend README、TODO 與 ROADMAP。

## Out of Scope

- 不做真正 async worker。
- 不做 queue、Redis、NATS、Celery、RQ 或 scheduler。
- 不做 job retry、dead letter queue、優先級或取消任務。
- 不接真正 OCR、embedding、Qdrant、rerank 或 LLM。
- 不做 PostgreSQL、資料庫 schema 或 migration。
- 不做登入、RBAC 或權限。
- 不新增獨立 job dashboard。

## Files likely to change

- `backend/app/schemas/documents.py`
- `backend/app/services/document_storage.py`
- `backend/app/api/routes/documents.py`
- `backend/tests/test_document_schemas.py`
- `backend/tests/test_documents.py`
- `frontend/src/api/client.ts`
- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] processing job schema 已定義並有 validation。
- [ ] mock OCR 執行時可保存或回傳對應 job metadata。
- [ ] document detail 可讀到文件相關 processing job 狀態。
- [ ] frontend 可顯示簡單 job status，不破壞既有 upload / OCR / RAG demo flow。
- [ ] metadata persistence 對舊文件有合理 default。
- [ ] 測試覆蓋 job schema、mock OCR job status 與既有 API 相容性。
- [ ] 文件明確說明目前 job contract 是同步 metadata，不是真正 worker。
- [ ] 未新增 Redis、NATS、Celery、RQ、Qdrant、embedding、LLM、PostgreSQL、登入或 RBAC。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`
