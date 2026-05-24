# 20-11 Frontend Minimal Chat Upload

## Goal

把 frontend demo 從工程 console 收斂成真正的最小產品入口：前台只保留客服問答與文件上傳兩個使用者可見區塊，其餘 OCR、chunking、indexing、document list、raw JSON 與 trace table 都留在 backend / CLI / API 層。

## Scope

- 調整既有 Vue single-page UI，只保留：
  - 客服問答輸入、回答與簡化引用來源。
  - 文件上傳入口與後端處理狀態摘要。
- 上傳成功後由 frontend 呼叫既有 backend mock OCR endpoint 完成 demo-safe ingestion，但不在 UI 顯示 OCR 細節。
- 移除使用者可見的 OCR panel、document list、metadata JSON、API response JSON、retrieval trace table 與 workflow dashboard。
- 更新 README、frontend README、TODO 與 ROADMAP，說明目前 frontend 只暴露 chat / upload，工程追蹤改由 backend API / CLI / docs 展示。

## Out of Scope

- 不新增 frontend route、router、登入、角色權限、後台權限隔離或 production admin console。
- 不新增 backend API endpoint、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、RBAC、Agent runtime 或 deployment。
- 不改變 `/rag/query` 預設 keyword baseline，不把 vector、rerank、hybrid 或 `hybrid_rerank` 接到 default frontend chat path。
- 不新增 sample data、eval dataset、PDF rendering、VLM parser、production OCR pipeline、streaming UI、demo media 或 release tag。

## Release Impact

- Target version: `v0.20.1` frontend UX clarification patch。
- Version bump required: no。
- 原因：本 ticket 只收斂既有 frontend UI 與文件說明，不新增 runtime 能力、不改 backend / frontend package version 或 Docker Compose `DOCURAG_VERSION`。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] Frontend 使用者可見主畫面只包含客服問答與文件上傳。
- [x] OCR、indexing、document list、metadata JSON、API response JSON 與 detailed trace table 不再出現在 frontend UI。
- [x] 上傳後 UI 只顯示後端已接收 / 已處理摘要，不顯示 OCR text 或 extracted fields。
- [x] RAG 回答仍顯示 answer、answer source、retrieval source 與簡化引用來源。
- [x] README / frontend README / TODO / ROADMAP 都明確說明 frontend 只暴露 chat / upload，其餘工程細節留在 backend / CLI。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- Local frontend demo view 檢查：畫面有客服問答與文件上傳，沒有 OCR panel、document list、metadata JSON、API response JSON、trace table，desktop viewport 無 horizontal overflow。
- `rg -n "Minimal Chat Upload|chat / upload|客服問答|文件上傳|20-11" README.md frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-20-interview-mvp-packaging/20-11-frontend-minimal-chat-upload.md`
- `git diff --check`

## Validation Result

- `npm.cmd run build` 於 `frontend/` 通過。
- Browser 檢查 `http://localhost:5174/` 通過：畫面標題只剩「文件客服助理」、「問問題」、「上傳文件」；未出現 OCR panel、document list、metadata JSON、API response JSON、trace table；desktop horizontal overflow 為 `0`。
- Ticket 指定 `rg` 通過。
- `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
