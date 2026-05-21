# v0.7.0 Local OCR Provider Adapter

## Goal

在既有 `OcrProvider` contract 後方接入 07-01 選定的本機 OCR provider，做出可驗證的 real OCR spike，同時保留 `mock` provider 與現有 API / frontend demo flow。

## Scope

- 新增或調整 backend OCR provider adapter，只接一個 07-01 選定 provider。
- 透過設定值選擇 `mock` 或 real OCR provider，預設仍使用安全的 `mock`。
- real provider 不可用時回傳清楚錯誤或 fallback，不讓 API crash。
- `POST /documents/{document_id}/ocr/mock` 既有 contract 保持相容；若新增 real OCR endpoint 或 provider switch，必須維持舊 demo 可用。
- OCR output 寫回既有 `OcrResult`、`processing`、`processing_jobs`、chunks 與 trace metadata。
- 新增 provider adapter 測試與失敗路徑測試。

## Out of Scope

- 不新增 async worker、queue、Redis、NATS、Celery 或 RQ。
- 不新增 Qdrant、embedding、rerank、LLM、OpenAI API、Ollama 或 vLLM。
- 不新增 PostgreSQL schema 或 migration。
- 不新增登入、權限或 RBAC。
- 不做大型 OCR quality tuning、PDF page rendering pipeline 或 image preprocessing pipeline。

## Implementation Notes

- 新增 `DOCURAG_OCR_PROVIDER` 設定，預設值為 `mock`。
- 新增 provider-selected `POST /documents/{document_id}/ocr`；既有 `POST /documents/{document_id}/ocr/mock` 保持相容。
- `DOCURAG_OCR_PROVIDER=mock` 時，provider-selected endpoint 走既有 `MockOcrProvider`。
- `DOCURAG_OCR_PROVIDER=paddleocr` 時，provider-selected endpoint 走 `PaddleOcrProvider`。
- `PaddleOcrProvider` 採 lazy import；未安裝 PaddleOCR dependency、模型初始化失敗、runtime 失敗或輸入不是 image file 時，會回傳 failed `OcrResult`，並由 real endpoint 轉成清楚的 `503`。
- real provider 失敗仍會先寫回 `ocr.status=failed`、`processing.ocr=failed`、`processing.failed_reason` 與 `processing_jobs` 的 `ocr_real` failed metadata。
- `backend[real-ocr]` optional extra、`DOCURAG_INSTALL_REAL_OCR` Docker build arg 與 Compose build arg 已加入；預設 build 不安裝 real OCR dependency，避免破壞 mock demo。

## Files likely to change

- `backend/app/core/config.py`
- `backend/app/services/ocr.py`
- `backend/app/services/document_storage.py`
- `backend/app/api/routes/documents.py`
- `backend/Dockerfile`
- `backend/pyproject.toml`
- `backend/tests/test_documents.py`
- `backend/tests/test_document_schemas.py`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] 可以透過設定選擇 `mock` 或 real OCR provider。
- [x] 預設行為不破壞 v0.6 mock OCR demo。
- [x] real provider 成功時會產生 `OcrResult` 並寫回 metadata。
- [x] real provider 失敗時會更新 processing status 與 processing job metadata。
- [x] 測試覆蓋 provider selection、成功路徑與失敗路徑。
- [x] 沒有引入 queue、DB、Qdrant、embedding、LLM 或權限系統。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`

## Validation Notes

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` passed: 42 tests passed.
- `cd frontend; npm.cmd run build` passed after rerunning outside the sandbox because sandbox file permissions blocked Vite config resolution.
- `docker build -t docurag-backend ./backend` blocked because Docker Desktop daemon was not running (`dockerDesktopLinuxEngine` pipe not found).
- `docker compose -f infra/docker-compose.yml up -d --build` and `docker compose -f infra/docker-compose.yml down` were also blocked by the same Docker daemon issue.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1` could not run because the Compose backend was not started.
- Mock OCR path remains covered by backend tests and remains the default provider path.
