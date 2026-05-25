# 27-03 Vector Source Expansion Contract

## Goal

固定 vector DB ingestion 的來源邊界，避免 Qdrant 只像是「OCR chunks 的向量庫」。長期合理目標是：

- 圖片 / 掃描文件：先透過 OCR 產生文字層，再切 chunks 與寫入 Qdrant。
- `.txt` / 純文字文件：直接以原文建立 chunks，不需要假裝經過 OCR。
- text-native PDF：後續可走 PDF text extraction，再建立 chunks。
- scanned PDF：需要 PDF rendering / OCR pipeline，不能在尚未實作時宣稱支援。

本 ticket 只建立 contract 與後續 implementation 邊界，不直接新增 PDF parser、PDF rendering 或新的外部依賴。

## Scope

- 定義 document text source taxonomy，例如 `ocr_image`、`text_upload`、`pdf_text`、`pdf_scanned_pending_ocr`。
- 定義 vector indexing service 應接受的 normalized text source contract：document id、source type、chunk text、page number、bbox、confidence、metadata。
- 明確規劃 `.txt` 檔應走 direct text chunking，不需要 OCR。
- 明確規劃 PDF 分流：text-native PDF 可走 future text extraction；scanned PDF 必須等 PDF rendering / OCR pipeline，不可直接宣稱已支援。
- 定義 Qdrant payload metadata 至少保留 `document_id`、`filename`、`chunk_id`、`source_type`、`content_source`、`page_number`、`created_at` 與 future project / tenant 欄位。
- 更新 README / docs / TODO / ROADMAP，讓 demo 說法清楚：目前 vector indexing 主要吃 OCR chunks；下一步會讓 text upload 成為 first-class source，PDF 需拆清楚 text PDF 與 scanned PDF。

## Out of Scope

- 不實作 PDF text extraction、PDF rendering、page image conversion、多頁 OCR pipeline 或 table reconstruction。
- 不新增新的 PDF / NLP / chunking 外部依賴。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth / RBAC、K8s 或 deployment 設定。
- 不修改 Qdrant collection vector size、embedding model、rerank algorithm 或 retrieval scoring。
- 不把 VLM structured fields 自動寫成 retrieval chunks；若未來要把欄位也索引，必須另開 ticket 定義 field-indexing policy。

## Release Impact

- Target version: none.
- Version bump required: no.
- 原因：本 ticket 是 source contract / planning ticket，只固定後續 implementation 的輸入邊界；不改 runtime 行為。

## Files likely to change

- `docs/api.md`
- `docs/architecture.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `tasks/phase-27-aggressive-defaults/27-03-vector-source-expansion-contract.md`

## Acceptance Criteria

- [x] 文件明確回答：vector DB 不應只長期依賴 OCR chunks；`.txt` 應支援 direct text chunks。
- [x] 文件明確區分 text-native PDF 與 scanned PDF，不把 PDF 支援說成單一簡單功能。
- [x] Vector source contract 包含 source type、page / bbox 可選欄位、content source metadata 與 future tenant / project metadata 位置。
- [x] 文件明確說明 VLM fields 不會在本 ticket 自動變成 retrieval chunks。
- [x] 後續 runtime ticket 可依此拆成 `.txt` direct ingestion、PDF text extraction、scanned PDF rendering / OCR 三個小任務。

## Validation

- `rg -n "text_upload|pdf_text|pdf_scanned|content_source|ocr_image|vector source|Vector Source" README.md backend/README.md frontend/README.md docs/api.md docs/architecture.md docs/ROADMAP.md TODO.md tasks/phase-27-aggressive-defaults`
- `git diff --check`

Validation result：

- Ticket `rg` passed.
- `git diff --check` passed（僅 Windows LF/CRLF 提示）。
