# 02-01 - Document Upload API

## Goal

建立文件上傳 API 的最小基礎，讓使用者可以建立 document record，並保留後續 OCR 與 RAG pipeline 的狀態欄位。

## Scope

- 定義 document upload endpoint。
- 支援建立最小 document record。
- 回傳 document id、filename、content type、size 與 status。
- status 初始值使用 `uploaded`。
- 加入 API 測試或手動驗證。

## Out of Scope

- 不實作 OCR。
- 不實作 RAG。
- 不建立 Qdrant indexing。
- 不觸發 Redis、NATS 或 background worker。
- 不實作登入、權限或資料庫 migration。
- 不建立 frontend upload UI。

## Files likely to change

- `backend/app/main.py`
- `backend/app/api/documents.py`
- `backend/app/schemas/documents.py`
- `backend/tests/test_documents.py`
- `docs/PRD.md`

## Acceptance Criteria

- [ ] 可呼叫 API 建立一筆 uploaded document。
- [ ] response 包含 document id、filename、content type、size、status。
- [ ] status 不會自動進入 OCR 或 indexing。
- [ ] validation 可證明 API contract 正常。

## Validation

- 執行 document API 測試。
- 手動呼叫 upload endpoint，確認 response 符合 acceptance criteria。
