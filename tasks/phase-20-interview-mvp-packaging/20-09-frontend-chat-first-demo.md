# 20-09 Frontend Chat-First Demo

## Goal

把既有 frontend demo 調整成面試更直覺的 customer chat-first 體驗：第一屏先像一般客服機器人一樣可以提問，文件上傳、OCR、文件列表與 JSON trace 則退到同頁的後台知識庫管理區。

## Scope

- 調整既有 Vue single-page UI 的資訊架構，讓 RAG chat 成為第一個主要互動區。
- 保留既有 upload、document list、OCR mock / selected OCR、metadata JSON、API response JSON 與 trace / citation 顯示。
- 將 upload / OCR / metadata 區塊以「後台知識庫管理」語意呈現，避免讓前台使用者體驗看起來像必須自行上傳文件。
- 更新 README、frontend README、TODO 與 ROADMAP，說明 demo 變成 chat-first，且 demo 前可用 seed script 預載公開 synthetic knowledge base。

## Out of Scope

- 不新增 frontend route、router、登入、角色權限、後台權限隔離或 production admin console。
- 不新增 backend API endpoint、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、RBAC、Agent runtime 或 deployment。
- 不改變 `/rag/query` 預設 keyword baseline，不把 vector、rerank、hybrid 或 `hybrid_rerank` 接到 default frontend chat path。
- 不新增 sample data、eval dataset、PDF rendering、VLM parser、production OCR pipeline、streaming UI 或 release tag。

## Release Impact

- Target version: `v0.20.1` frontend demo UX patch。
- Version bump required: no。
- 原因：本 ticket 只重排既有 frontend demo UI 與文件說明，不新增 runtime 能力、不改 backend / frontend package version 或 Docker Compose `DOCURAG_VERSION`。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] Frontend 第一屏以客服 / Viewer RAG chat 為主，使用者不需要先看到 upload / OCR 才理解怎麼提問。
- [x] 當尚未 seed 或尚未有可查詢文件時，chat 區塊以中文 empty state 指向後台知識庫建置或 `scripts/seed-demo-data.ps1`。
- [x] Upload、OCR、document list、metadata JSON 與 API response JSON 仍可在同頁後台管理區使用。
- [x] Trace、citations 與 retrieved chunks 仍在回答後可見，且不新增 backend API、frontend route 或外部依賴。
- [x] README / frontend README / TODO / ROADMAP 都明確說明 chat-first demo 與後台文件建置的分工。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- Local frontend demo view 檢查：第一屏為 chat-first、後台區塊仍可上傳 / OCR / 選文件、desktop viewport 無 horizontal overflow。
- `rg -n "chat-first|客服|後台知識庫|20-09" README.md frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-20-interview-mvp-packaging/20-09-frontend-chat-first-demo.md`
- `git diff --check`

## Validation Result

- [x] `npm.cmd run build` 於 `frontend/` 通過。
- [x] Local frontend demo view 檢查通過：第一屏顯示 `前台客服機器人`，同頁仍有 `後台知識庫管理`、`上傳文件`、OCR、文件列表與 JSON 區塊；desktop viewport horizontal overflow 為 `0`。
- [x] 在既有 local demo data 下送出 `payment due date Net 15`，回答後可見 `回答`、`引用來源`、`檢索追蹤`、`檢索片段`，且 evidence 包含 `Net 15` / `2026-06-15` / `AUR-2026-051`。
- [x] `rg -n "chat-first|客服|後台知識庫|20-09" README.md frontend/README.md TODO.md docs/ROADMAP.md tasks/phase-20-interview-mvp-packaging/20-09-frontend-chat-first-demo.md` 通過。
- [x] `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
