# v0.6.0 Processing Status Contract

## Goal

補齊文件處理狀態契約，讓 upload、OCR、chunking / indexing 與 ready / failed 的流轉更清楚，為後續真正 OCR、embedding indexing 與 background worker 做準備。

## Scope

- 檢視目前 `DocumentStatus`、`OcrStatus` 與 frontend status 顯示。
- 定義文件處理狀態流轉，至少涵蓋 upload、OCR pending / running / completed / failed、indexing pending / completed、ready 與 failed。
- 以最小改動更新 backend schema、metadata persistence 與 frontend status display。
- 保留既有 mock OCR 與 local keyword RAG demo flow。
- 文件中說明狀態只是 contract，尚未代表真正 async worker。
- 補上 schema validation、狀態流轉與既有 API 相容性測試。
- 更新 README、backend README、frontend README、TODO 與 ROADMAP。

## Out of Scope

- 不做真正 background worker。
- 不做 Redis、NATS、Celery、RQ 或 task queue。
- 不接真正 OCR engine。
- 不做 embedding、Qdrant、rerank 或 LLM。
- 不做 database migration。
- 不做登入、RBAC 或權限。
- 不新增複雜 workflow engine；只定義目前需要的狀態 contract。

## Files likely to change

- `backend/app/schemas/documents.py`
- `backend/app/services/document_storage.py`
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

- [ ] 文件處理狀態流轉已在 schema 與文件中明確定義。
- [ ] upload 後的初始狀態清楚表示尚未完成 OCR / indexing。
- [ ] mock OCR 完成後狀態能清楚表示 OCR completed 與 chunks available。
- [ ] RAG query 對未完成 OCR / indexing 的文件行為仍可預期。
- [ ] frontend status 顯示能區分文件整體狀態與 OCR 狀態。
- [ ] 舊 metadata 若缺少新增欄位仍能用合理 default 讀取。
- [ ] 測試覆蓋狀態 default、狀態流轉與 API response。
- [ ] 文件明確說明目前沒有真正 async worker 或外部 queue。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`
