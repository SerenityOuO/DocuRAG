# README Image Refresh

## Goal

使用使用者提供的兩張 demo 截圖，將 root `README.md` 更新為更精簡的繁中展示入口，讓面試官可以快速理解專案用途、畫面與啟動方式。

## Scope

- 將兩張使用者提供的截圖保存到 `docs/demo-media/`，並由 `README.md` 使用相對路徑引用。
- 參考 `jason211346/OllamaChat` README 的簡潔結構，保留標題、短介紹、截圖、功能、需求、啟動、使用方式、技術棧與 API 說明。
- `README.md` 內容使用繁體中文，並保留開頭連到 `README_DEV.md` 的入口。
- 更新 `TODO.md` 的 Documentation Maintenance checklist。

## Out of Scope

- 不修改 backend、frontend、scripts、sample data、infra 或 runtime 行為。
- 不新增 OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限、資料庫 schema、worker 或 deployment 能力。
- 不更新 backend / frontend version、Docker Compose `DOCURAG_VERSION`、release tag 或 release artifact。
- 不把 `README_DEV.md` 的長篇 release log 回填到 root `README.md`。

## Release Impact

- Target version: none.
- Version bump required: no.
- 原因：本 ticket 只更新 README 展示敘事與圖片資產，不改 runtime、API、版本或 release artifact。

## Files likely to change

- `README.md`
- `TODO.md`
- `docs/demo-media/readme-viewer-query.jpg`
- `docs/demo-media/readme-admin-ingestion.jpg`
- `tasks/docs-readme-image-refresh.md`

## Acceptance Criteria

- [x] `README.md` 開頭保留連到 `README_DEV.md` 的超連結。
- [x] `README.md` 引用兩張使用者提供的 demo 截圖。
- [x] `README.md` 以繁中短版內容說明功能、需求、啟動、使用方式、技術棧、API 與邊界。
- [x] 本 ticket 不修改任何程式碼或 runtime 設定。

## Validation

- `rg -n "readme-viewer-query.jpg|readme-admin-ingestion.jpg|文件知識庫問答|README_DEV.md" README.md TODO.md tasks/docs-readme-image-refresh.md`
- `git diff --check`

## Validation Result

- [x] `rg -n "readme-viewer-query.jpg|readme-admin-ingestion.jpg|文件知識庫問答|README_DEV.md" README.md TODO.md tasks/docs-readme-image-refresh.md` 通過。
- [x] `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
