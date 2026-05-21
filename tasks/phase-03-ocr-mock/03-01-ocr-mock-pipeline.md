# v0.4.0 OCR Mock Pipeline

## Goal

建立可驗證的 OCR mock pipeline，讓已上傳文件可以執行 mock OCR、查詢 OCR 結果，並在 frontend 顯示 OCR status、OCR text 與 extracted fields。

## Scope

- 新增 `POST /documents/{document_id}/ocr/mock`。
- 新增 `GET /documents/{document_id}/ocr`。
- 將 OCR mock result 保存到 local JSON metadata store。
- frontend 文件詳情可觸發 Run Mock OCR。
- frontend 顯示 OCR status、OCR text 與 extracted fields。
- 更新 v0.4.0 相關文件、TODO 與版本號。

## Out of Scope

- 不接 PaddleOCR、Tesseract、VLM 或任何真正 OCR engine。
- 不做 RAG、embedding、rerank 或 citation generation。
- 不做 Qdrant、Redis、NATS、vLLM 或 worker queue。
- 不做登入、RBAC、PostgreSQL、資料庫 schema 或 migration。
- 不做 production storage、multi-user isolation 或 async job orchestration。

## Files likely to change

- `backend/app/schemas/documents.py`
- `backend/app/services/document_storage.py`
- `backend/app/api/routes/documents.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_document_schemas.py`
- `frontend/src/api/client.ts`
- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `backend/README.md`
- `frontend/README.md`
- `backend/pyproject.toml`
- `backend/app/core/config.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `infra/docker-compose.yml`

## Acceptance Criteria

- [x] `POST /documents/{document_id}/ocr/mock` 對存在的文件產生 deterministic mock OCR text 與 extracted fields。
- [x] `POST /documents/{document_id}/ocr/mock` 對不存在的文件回傳 404。
- [x] `GET /documents/{document_id}/ocr` 回傳已保存的 OCR result。
- [x] `GET /documents/{document_id}/ocr` 對尚未執行 OCR 的文件回傳 pending/not_run 狀態。
- [x] OCR result 寫入 `data/documents.json` 的對應 document metadata。
- [x] frontend 可以對選中的文件按 Run Mock OCR。
- [x] frontend 顯示 OCR status、OCR text 與 extracted fields。
- [x] backend pytest 通過。
- [x] frontend build 通過。
- [x] Docker build 通過。
- [x] Docker Compose 啟動後 `/health`、upload 與 OCR mock API 都可驗證。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `curl http://127.0.0.1:8000/health`
- `curl -X POST http://127.0.0.1:8000/documents/upload -F "file=@sample.txt"`
- `curl -X POST http://127.0.0.1:8000/documents/{document_id}/ocr/mock`
- `curl http://127.0.0.1:8000/documents/{document_id}/ocr`
- `docker compose -f infra/docker-compose.yml down`
