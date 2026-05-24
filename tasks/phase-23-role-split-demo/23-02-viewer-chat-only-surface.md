# 23-02 Viewer Chat Only Surface

## Goal

將 frontend 的預設入口收斂為 Viewer Chat：使用者進入首頁時只看到問答、answer source、retrieval source、citation summary 與必要的空狀態，不再在 Viewer 主畫面看到文件上傳或 OCR 操作。

## Scope

- 調整既有 Vue frontend，讓預設首頁或主要 viewport 成為 Chat-only Viewer surface。
- 移除 Viewer 主畫面的 upload / OCR CTA、mock fallback 操作、document ingestion wording 與任何會讓人以為「一般使用者直接上傳圖片問答」的敘事。
- 保留既有 `/rag/query` API contract、answer source、retrieval source、citations 與必要錯誤狀態。
- 空知識庫狀態需提示「目前沒有可查詢內容，請先由後台知識庫管理流程建立資料」，但不要在 Viewer surface 直接提供上傳。
- 補 frontend build / UI smoke 所需檢查。

## Out of Scope

- 不新增 backend API、route guard、登入、RBAC 或權限判斷。
- 不修改 OCR provider、RAG retrieval algorithm、LLM generation、sample data、eval runner 或 smoke script。
- 不實作 production trace dashboard、strategy comparison page、streaming chat、multi-session chat history 或 Agent UI。
- 不刪除後台 ingestion 功能；後台入口由 `23-03` 處理。

## Release Impact

- Target version: `v0.23.0`
- Version bump required: no
- 原因：本 ticket 是 Phase 23 的 frontend 子切片；完整 role split 與 release sync 由 `23-04` 完成。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `frontend/README.md`
- `TODO.md`

## Acceptance Criteria

- [x] Frontend 預設畫面是 Viewer Chat，不顯示文件上傳、OCR、mock fallback 或 ingestion 操作。
- [x] Chat query 成功後仍能顯示 answer、answer source、retrieval source 與 citation summary。
- [x] 空知識庫 / 無 chunks 狀態以 Viewer 角度說明，不把使用者導向同一畫面的上傳操作。
- [x] UI 文字明確使用「前台查詢」或等價語意，不暗示 OCR 在前端執行。
- [x] 既有 frontend build 通過。

## Validation

- `cd frontend; npm.cmd run build`
- Browser 檢查 local frontend：首頁沒有 upload / OCR controls，RAG query result 仍顯示 answer 與 citations。
- `rg -n "上傳|OCR|mock|知識庫管理|Admin|Analyst|Viewer|citation|answer source" frontend/src frontend/README.md TODO.md`
- `git diff --check`
