# 20-08 README Zh-TW Demo Media Refresh

## Goal

用 20-07 中文化後的 frontend demo 重新覆蓋 README 引用的前端截圖，讓 README media 與目前繁中 UI 一致。

## Scope

- 重新截取並覆蓋 README 已引用的 frontend demo 圖：
  - `docs/demo-media/frontend-overview.png`
  - `docs/demo-media/frontend-trace.png`
- 確認 README 仍引用既有 demo media 路徑，不新增圖片路徑或 README 結構。
- 同步更新本 ticket、`TODO.md` 與 `docs/ROADMAP.md` 的完成狀態。

## Out of Scope

- 不修改 frontend UI、route、API、backend runtime、sample data、smoke script 或 eval runner。
- 不重新設計 README、不新增 GIF、不新增 production eval dashboard、strategy comparison page 或 export UI。
- 不新增 backend API endpoint、frontend route、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、Agent runtime 或 deployment。

## Release Impact

- Target version: `v0.20.1` README media refresh patch。
- Version bump required: no。
- 原因：本 ticket 只同步 README demo media，讓圖片跟上既有繁中 UI，不形成新的 runtime release artifact；不更新 backend / frontend package version 或 Docker Compose `DOCURAG_VERSION`。

## Files likely to change

- `docs/demo-media/frontend-overview.png`
- `docs/demo-media/frontend-trace.png`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] `frontend-overview.png` 顯示 20-07 後的繁中 UI hero、summary cards、workflow 與主要 panels。
- [x] `frontend-trace.png` 顯示 20-07 後的繁中 RAG answer、retrieval trace、citations / chunks 區域。
- [x] README 仍引用既有 demo media 路徑。
- [x] 不新增 route、API、外部依賴或 out-of-scope runtime。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- Local frontend demo view 檢查並重新產出 `docs/demo-media/frontend-overview.png` 與 `docs/demo-media/frontend-trace.png`
- `rg -n "frontend-overview.png|frontend-trace.png|eval-summary.png" README.md`
- `git diff --check`

## Validation Result

- [x] `npm.cmd run build` 於 `frontend/` 通過。
- [x] Local frontend demo view 重新截取 `docs/demo-media/frontend-overview.png` 與 `docs/demo-media/frontend-trace.png`；頁面標題為 `DocuRAG AgentOps 文件智能平台`，主要中文 panel / trace 可見，舊英文可見標籤未出現在 rendered text，desktop viewport 無 horizontal overflow。
- [x] `rg -n "frontend-overview.png|frontend-trace.png|eval-summary.png" README.md` 通過，README 仍引用既有三張 demo media。
- [x] `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
