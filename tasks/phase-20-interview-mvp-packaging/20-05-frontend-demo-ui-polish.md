# 20-05 Frontend Demo UI Polish

## Goal

改善既有 Vue demo UI 的視覺質感與面試展示可讀性，讓 upload -> OCR -> RAG -> citation -> trace 的流程在第一眼更像完整產品介面。

## Scope

- 只調整既有 single-page frontend layout、CSS、文案密度與狀態呈現。
- 保留既有 API contract、資料流、component 邊界與 demo 操作流程。
- 增加不依賴新 API 的 summary / workflow UI，讓面試時更容易講解目前 MVP 狀態。
- 不新增外部依賴、不新增 route、不修改 backend。

## Out of Scope

- 不新增 production eval dashboard、strategy comparison page、live eval runner 或 export UI。
- 不新增 backend API endpoint、frontend route、外部套件、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC 或 Agent runtime。
- 不新增 VLM parser、PDF rendering、production OCR pipeline、K8s、deployment 設定或 release tag。
- 不改 retrieval algorithm、RAG response contract、eval runner 或 smoke script。

## Release Impact

- Target version: `v0.20.1` frontend polish patch。
- Version bump required: no。
- 原因：本 ticket 只改善面試 demo UI 質感，不形成新的 runtime release artifact；不更新 backend / frontend package version 或 Docker Compose `DOCURAG_VERSION`。

## Files likely to change

- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] 第一屏能清楚呈現 MVP 狀態、backend health、文件數、目前選取文件與 RAG answer source。
- [x] 既有 upload、document list、OCR、RAG chat、citations、retrieved chunks 與 trace panel 操作保持可用。
- [x] 視覺風格更接近面試展示用 AI application dashboard，且 desktop viewport 不出現明顯重疊。
- [x] 不新增 route、API、外部依賴或 out-of-scope runtime。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- Browser 檢查 local frontend demo view 可正常顯示。
- `git diff --check`

Validation result：

- `npm.cmd run build` 於 `frontend/` 通過。
- Browser 檢查 `http://localhost:5173/` local frontend demo view，desktop viewport 無 horizontal overflow。
- `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
