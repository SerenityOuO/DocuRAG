# 24-01 Parser Contract

## Goal

固定 Phase 24 的 VLM-compatible parser contract，定義 OCR text 如何轉成 invoice structured fields、parser status、trace metadata 與 fallback 行為；本 ticket 只做規格與邊界，不實作 runtime。

## Scope

- 定義 `DocumentFields` / `ExtractedField` / `ParserResult` 的最小欄位集合。
- 定義 invoice MVP 欄位：`document_type`、`vendor_name`、`invoice_number`、`issue_date`、`total_amount`、`tax_amount`、`currency`、`line_items`。
- 定義欄位層級 metadata：`confidence`、`source_text`、`source_page`、`source_bbox`、`parser_source` 與 `fallback_reason`。
- 定義 document processing status 如何表達 `parsing`、`parsed` 與 parser failure。
- 定義後續 API contract 草案：`POST /documents/{document_id}/parse` 與 `GET /documents/{document_id}/fields`。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 24 contract 狀態。

## Out of Scope

- 不實作 parser service、backend API、frontend UI 或 smoke script。
- 不接真正 VLM、Ollama vision call、OpenAI-compatible VLM、LLM parser 或新外部依賴。
- 不修改 PaddleOCR provider、OCR normalization、chunking、RAG retrieval、eval runner 或 Qdrant indexing。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC 或 Agent runtime。
- 不實作人工修正欄位、欄位版本紀錄、audit log、表格完整重建、PDF rendering 或多頁 production OCR pipeline。

## Release Impact

- Target version: `v0.24.0` planning backlog。
- Version bump required: no。
- 原因：本 ticket 只固定 parser contract；Phase 24 runtime 與 release sync 由後續 tickets 完成。

## Files likely to change

- `docs/ROADMAP.md`
- `TODO.md`
- `docs/api.md`
- `docs/architecture.md`

## Acceptance Criteria

- [ ] 文件明確定義 invoice structured fields contract。
- [ ] 文件明確定義 parser status、fallback metadata 與 source trace 欄位。
- [ ] 文件明確區分 deterministic parser MVP、future LLM parser 與 future VLM parser。
- [ ] 文件不宣稱 Phase 24 已完成 production VLM parser。

## Validation

- `rg -n "v0.24.0|Phase 24|Parser|VLM-compatible|DocumentFields|ExtractedField|fallback_reason" README.md TODO.md docs/ROADMAP.md docs/api.md docs/architecture.md tasks/phase-24-vlm-parser-mvp/24-01-parser-contract.md`
- `git diff --check`
