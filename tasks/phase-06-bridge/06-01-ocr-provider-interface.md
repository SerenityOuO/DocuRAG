# v0.6.0 OCR Provider Interface Bridge

## Goal

把目前的 OCR mock 流程整理成可替換的 OCR provider 邊界，讓後續接 PaddleOCR、Tesseract 或 VLM parser 時，不需要重寫既有 upload、document detail、OCR result API 與 frontend 流程。

## Scope

- 建立最小 OCR provider / service 邊界，先只保留 `mock` provider。
- 將 deterministic mock OCR text 與 extracted fields 的產生邏輯從 `DocumentStorage` 中移到 OCR provider / service 邊界。
- 保留既有 `POST /documents/{document_id}/ocr/mock` 與 `GET /documents/{document_id}/ocr` 行為。
- 保留 OCR result 寫入 local JSON metadata store 的行為。
- 保留 frontend `Run Mock OCR` 流程，不改成真正 OCR。
- 補上 provider 邊界、mock OCR result 與既有 endpoint 相容性的測試。
- 更新 README、backend README、TODO 與 ROADMAP，說明目前仍只有 mock provider。

## Out of Scope

- 不接 PaddleOCR、Tesseract、VLM 或任何真正 OCR engine。
- 不新增 OCR library 或模型權重。
- 不做圖片前處理、PDF rendering、版面分析或表格抽取。
- 不做 async worker、queue、Redis 或 NATS。
- 不做 embedding、Qdrant、RAG provider 或 LLM。
- 不做 PostgreSQL、資料庫 schema 或 migration。
- 不做登入、RBAC 或權限。
- 不建立過度抽象的 provider registry；只做目前會用到的最小邊界。

## Files likely to change

- `backend/app/services/document_storage.py`
- `backend/app/services/ocr.py`
- `backend/app/api/routes/documents.py`
- `backend/app/core/config.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_document_schemas.py`
- `README.md`
- `backend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] mock OCR 產生邏輯已移入明確的 OCR provider / service 邊界。
- [ ] `DocumentStorage` 不再負責組 mock OCR text，只負責保存與讀取 document metadata。
- [ ] `POST /documents/{document_id}/ocr/mock` response 與 v0.5.1 相容。
- [ ] `GET /documents/{document_id}/ocr` response 與 v0.5.1 相容。
- [ ] OCR result 仍保存到 `data/documents.json`。
- [ ] 測試覆蓋 mock provider output、404 行為與 metadata persistence。
- [ ] 文件明確說明目前只有 mock provider，尚未接真正 OCR 模型。
- [ ] 未新增 PaddleOCR、Tesseract、VLM、embedding、Qdrant、Redis、NATS、PostgreSQL、登入或 RBAC。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `docker build -t docurag-backend ./backend`
- `docker compose -f infra/docker-compose.yml up -d --build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `docker compose -f infra/docker-compose.yml down`
- `git status --short --branch`
