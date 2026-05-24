# 24-03 Document Fields API

## Goal

新增最小 parse / fields API，讓既有 document OCR result 可以觸發 invoice parser，並把 structured fields 保存到 local JSON metadata store。

## Scope

- 新增 `POST /documents/{document_id}/parse`，對已完成 OCR 的 document 執行 parser。
- 新增或補齊 `GET /documents/{document_id}/fields`，回傳目前保存的 parser result。
- 將 parser result 保存到既有 local JSON metadata store。
- 解析成功時更新 document processing status / processing job metadata，解析失敗時保留明確錯誤與 fallback reason。
- 新增 backend API tests，覆蓋未 OCR、OCR 後 parse、fields lookup、document not found 與 parser missing fields。
- 更新 `docs/api.md`、`TODO.md` 與 `docs/ROADMAP.md`。

## Out of Scope

- 不修改 frontend UI；UI 留給 `24-04`。
- 不新增真正 VLM、LLM parser、Ollama vision call、OpenAI-compatible VLM 或新外部依賴。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC 或 Agent runtime。
- 不讓 parser 自動觸發 vector indexing、RAG ingestion、Qdrant upsert 或 eval run。
- 不實作人工修正欄位、欄位版本紀錄、audit log、PDF rendering、多頁 production OCR pipeline 或表格完整重建。

## Release Impact

- Target version: `v0.24.0`。
- Version bump required: no。
- 原因：本 ticket 新增 Phase 24 API slice，但完整 demo / release sync 留給 `24-05`。

## Files likely to change

- `backend/app/api/routes/documents.py`
- `backend/app/schemas/documents.py`
- `backend/app/services/document_parser.py`
- `backend/app/services/document_storage.py`
- `backend/tests/test_documents.py`
- `backend/tests/test_document_parser.py`
- `docs/api.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] `POST /documents/{document_id}/parse` 可對已 OCR document 產生 structured fields。
- [ ] `GET /documents/{document_id}/fields` 可回傳保存的 parser result。
- [ ] 未完成 OCR 的 document 會明確失敗，不會產生空假資料。
- [ ] Parser result 保存於 local JSON metadata store，重啟後仍可查詢。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `rg -n "/parse|/fields|ParserResult|DocumentFields|fallback_reason" backend/app backend/tests docs/api.md TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-03-document-fields-api.md`
- `git diff --check`
