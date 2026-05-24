# 24-02 Invoice Parser Service

## Goal

實作最小 deterministic invoice parser service，從既有 OCR text 抽出 demo-safe invoice structured fields，作為 future VLM / LLM parser 的穩定 fallback。

## Scope

- 新增或擴充 backend schema，承接 `ParserResult`、`DocumentFields` 與 `ExtractedField`。
- 新增 deterministic invoice parser service，從 OCR text / OCR lines 抽取 invoice MVP 欄位。
- Parser 必須保留欄位來源資訊，例如 matched source text、page 與 confidence。
- Parser 找不到欄位時必須回傳明確 missing / fallback metadata，而不是產生假資料。
- 新增 backend unit tests，覆蓋 sample invoice OCR text、missing field、中文 / 英文標籤與金額格式。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 24-02 狀態。

## Out of Scope

- 不新增 backend parse API endpoint；API 留給 `24-03`。
- 不修改 frontend UI；UI 留給 `24-04`。
- 不接真正 VLM、Ollama vision call、OpenAI-compatible VLM、LLM parser 或新外部依賴。
- 不修改 OCR provider、PaddleOCR model、OCR preprocessing、chunk generation、RAG retrieval 或 eval runner。
- 不新增 PostgreSQL、Redis、NATS、worker、async queue、Auth、RBAC、Agent runtime 或 deployment。
- 不實作人工修正、欄位版本紀錄、audit log、表格完整重建、多頁 PDF parser 或 production parser tuning。

## Release Impact

- Target version: `v0.24.0`。
- Version bump required: no。
- 原因：本 ticket 只新增 parser service building block；Phase 24 release sync 由 `24-05` 完成。

## Files likely to change

- `backend/app/schemas/documents.py`
- `backend/app/services/document_parser.py`
- `backend/app/services/document_storage.py`
- `backend/tests/test_document_parser.py`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Parser 可從 sample invoice OCR text 抽出 invoice number、date、total amount 與 currency。
- [ ] Parser result 包含 `parser_source`、`confidence`、`source_text` 與 fallback metadata。
- [ ] Missing field 不會被硬填假值。
- [ ] Backend tests 覆蓋成功與缺欄位案例。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "DocumentFields|ExtractedField|ParserResult|document_parser|fallback_reason" backend/app backend/tests TODO.md docs/ROADMAP.md tasks/phase-24-vlm-parser-mvp/24-02-invoice-parser-service.md`
- `git diff --check`
