# 02-02 - Document Metadata Schema

## Goal

定義文件 metadata schema，讓 document upload、後續 OCR、解析與索引狀態有一致欄位可使用。

## Scope

- 定義 document metadata 欄位。
- 定義 document status enum。
- 補充 request / response schema。
- 確認 schema 可支援後續 OCR 與 RAG，但不實作 pipeline。

## Out of Scope

- 不建立資料庫 migration。
- 不實作 ORM model。
- 不接 PostgreSQL。
- 不實作 OCR、parser、chunking、embedding 或 Qdrant。
- 不實作 Redis、NATS 或 worker。
- 不實作 RBAC。

## Files likely to change

- `backend/app/schemas/documents.py`
- `backend/tests/test_document_schemas.py`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`

## Acceptance Criteria

- [ ] schema 包含 document id、project id、filename、file type、content type、size、status、created at。
- [ ] status enum 至少包含 `uploaded`、`processing`、`ready`、`failed`。
- [ ] schema 測試涵蓋有效與無效 status。
- [ ] 沒有新增資料庫 schema 或 migration。

## Validation

- 執行 schema 測試。
- 人工檢查沒有新增 database migration 或外部服務設定。
