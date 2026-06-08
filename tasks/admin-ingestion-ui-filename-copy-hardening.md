# Admin Ingestion UI Filename and Copy Hardening

## Goal

修正後台資料匯入狀態中容易誤解的檔名與欄位修正文案，讓中文檔名可正常顯示，並把 human correction 表單改成一般使用者看得懂的中文。

## Scope

- 修正 upload filename sanitization，避免中文檔名如 `周峻緯履歷.pdf` 被保存成 `pdf`。
- 後台資料匯入狀態顯示完整文件名稱，來源標籤只表示來源類型。
- 將 `corrected value`、`reviewer reason`、`golden label` 等 UI 文案改成中文說法。
- 補充 focused backend filename test 與 frontend build validation。

## Out of Scope

- 不新增 document delete API、文件刪除按鈕或 destructive edit / delete flow。
- 不修改 OCR、VLM parser、RAG ranking、Agent、Auth / RBAC、資料庫 schema、migration、worker 或 deployment。
- 不回推修改既有已保存錯誤檔名的 metadata；舊紀錄若原始檔名已遺失，需重新上傳或另開資料修復 ticket。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是小範圍 UI / filename hardening，不改 release 版本。

## Files likely to change

- `backend/app/services/document_storage.py`
- `backend/tests/test_documents.py`
- `frontend/src/App.vue`
- `README_DEV.md`
- `TODO.md`
- `tasks/admin-ingestion-ui-filename-copy-hardening.md`

## Acceptance Criteria

- [x] 中文檔名上傳後 `filename` 保留完整名稱與副檔名。
- [x] 後台資料匯入狀態明確顯示文件名稱，來源標籤不被誤看成檔名。
- [x] 欄位修正表單使用中文文案，使用者可理解要填修正後欄位值與修正原因。
- [x] 不新增文件刪除功能。

## Validation

- `python -m pytest backend/tests/test_documents.py -q`
- `npm.cmd run build`
- `rg -n "周峻緯履歷|修正後欄位值|修正原因|標準答案|document delete|destructive edit" backend frontend README_DEV.md TODO.md tasks/admin-ingestion-ui-filename-copy-hardening.md`
- `git diff --check`

## Completion Notes

- Backend filename sanitization 改為保留 Unicode word characters，`周峻緯履歷.pdf` 會保存為完整 `filename`。
- Frontend 後台資料匯入狀態改用 `documentDisplayName()` 顯示文件名稱，來源 pill 改成 `來源：PDF 文字` 這類來源類型。
- Human correction 表單改成「修正後欄位值」、「修正原因」、「保存標準答案」，並保留 backend 的 correction / golden label API contract。
- 本 ticket 未新增文件刪除功能；真正 document delete 仍需另開 ticket 定義 API、權限、資料安全與 validation。
- Validation 已通過：`python -m pytest backend/tests/test_documents.py -q`、`npm.cmd run build`。
