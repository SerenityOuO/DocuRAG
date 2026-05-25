# 28-01 Document Source Router Contract

## Goal

固定 Phase 28 的文件來源路由，讓上傳後的處理方式不要全部硬塞進 OCR：

- 圖片：走既有 provider-selected OCR，產生 OCR text / OCR lines / chunks。
- `.txt`：直接讀原文並建立 chunks，不再假裝是 OCR 結果。
- text-native PDF：走 PDF text extraction，再建立 chunks。
- scanned PDF：需要 PDF rendering / OCR pipeline，未實作前只能標示 pending / unsupported，不可宣稱已支援。

本 ticket 是 Phase 28 的 contract ticket，目標是先把路徑講清楚，讓後續 runtime ticket 不會把 PDF、txt、OCR、VLM 混在一起。

## Scope

- 定義 source router contract：依 `file_type` / `content_type` / future detection result 決定 `image_ocr`、`text_upload`、`pdf_text` 或 `pdf_scanned_pending_ocr`。
- 定義 normalized document text contract，至少包含 document id、source type、text、page number、bbox、confidence、metadata 與 created time。
- 明確規定 `.txt` direct ingestion 不需要 OCR job，也不應使用 `ocr_mock` 當 source。
- 明確規定 PDF 必須分成 text-native PDF 與 scanned PDF；scanned PDF 需要 PDF rendering / OCR 後續 ticket。
- 定義 frontend ingestion flow 應依 source type 顯示不同狀態：text 可直接建立知識庫，image 需 OCR，PDF 若尚未支援 extraction 要顯示清楚原因。
- 更新 README、backend README、frontend README、docs/api.md、docs/architecture.md、docs/demo-script.md、TODO.md 與 docs/ROADMAP.md 的 Phase 28 說法。

## Out of Scope

- 不實作 `.txt` runtime ingestion；留給 `28-02`。
- 不實作 PDF text extraction；留給 `28-03`。
- 不實作 PDF rendering、多頁 OCR pipeline、layout analysis、table reconstruction 或 scanned PDF OCR。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、K8s 或 deployment 設定。
- 不新增正式 Auth / RBAC；login mode 留給 `28-04`。
- 不修改 embedding model、Qdrant collection vector size、rerank algorithm 或 Agent planner。

## Release Impact

- Target version: none.
- Version bump required: no.
- 原因：本 ticket 只固定 Phase 28 source routing contract，不改 runtime 行為。

## Files likely to change

- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `tasks/phase-28-document-sources-auth-mode/28-01-document-source-router.md`

## Acceptance Criteria

- [x] 文件明確回答 `.txt` 不應再透過 mock OCR 變成 chunks。
- [x] 文件明確回答 PDF 不是單一路徑，必須分成 text-native PDF 與 scanned PDF。
- [x] Source router contract 明確列出 `image_ocr`、`text_upload`、`pdf_text`、`pdf_scanned_pending_ocr`。
- [x] Frontend flow 說法清楚區分：text 直接進知識庫、image 先 OCR、PDF 依可抽文字與否分流。
- [x] 文件明確說明本 ticket 不新增 worker、DB、正式 auth 或 production PDF pipeline。

## Validation

- `rg -n "image_ocr|text_upload|pdf_text|pdf_scanned_pending_ocr|source router|Document Source Router" README.md backend/README.md frontend/README.md docs/api.md docs/architecture.md docs/demo-script.md TODO.md docs/ROADMAP.md tasks/phase-28-document-sources-auth-mode`
- `git diff --check`

Validation result：

- Ticket `rg` passed.
- `git diff --check` passed（僅 Windows LF/CRLF 提示）。
