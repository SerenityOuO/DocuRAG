# 20-06 README Demo Media Refresh

## Goal

用 20-05 polish 後的前端畫面重新產生 README 使用的 demo media，讓面試第一眼看到的截圖與目前 UI 質感一致。

## Scope

- 只覆蓋既有 README 引用的三張 demo 圖：
  - `docs/demo-media/frontend-overview.png`
  - `docs/demo-media/frontend-trace.png`
  - `docs/demo-media/eval-summary.png`
- 使用既有 backend / frontend / smoke script / sample data 產生畫面與 eval summary。
- 同步更新本 ticket、`TODO.md` 與 `docs/ROADMAP.md` 的完成狀態。
- 不修改 frontend 原始碼、不新增 route、不新增 API、不新增外部依賴。

## Out of Scope

- 不新增 production eval dashboard、strategy comparison page、live eval runner、export UI 或 README GIF。
- 不新增 backend API endpoint、frontend route、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC 或 Agent runtime。
- 不新增 VLM parser、PDF rendering、production OCR pipeline、K8s、deployment 設定或 release tag。
- 不修改 retrieval algorithm、RAG response contract、eval runner、sample data 或 smoke script。

## Release Impact

- Target version: `v0.20.1` media refresh patch。
- Version bump required: no。
- 原因：本 ticket 只刷新 README demo 圖與文件狀態，不形成新的 runtime release artifact；不更新 backend / frontend package version 或 Docker Compose `DOCURAG_VERSION`。

## Files likely to change

- `docs/demo-media/frontend-overview.png`
- `docs/demo-media/frontend-trace.png`
- `docs/demo-media/eval-summary.png`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] README 引用的 frontend overview 截圖反映 20-05 polish 後的第一屏質感。
- [x] README 引用的 frontend trace 截圖反映新版 RAG answer、retrieval trace、citations 與 chunks 呈現。
- [x] README 引用的 eval summary 圖反映目前 retrieval eval baseline summary。
- [x] 不新增 route、API、外部依賴或 out-of-scope runtime。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- Browser 檢查 local frontend demo view 並重新截取 README demo media。
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1`
- `rg -n "frontend-overview.png|frontend-trace.png|eval-summary.png" README.md`
- `git diff --check`

Validation result：

- `npm.cmd run build` 於 `frontend/` 通過。
- Browser 檢查 `http://localhost:5173/` local frontend demo view，並覆蓋 `frontend-overview.png` 與 `frontend-trace.png`。
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./scripts/retrieval-eval-smoke.ps1` 通過，keyword summary：`case_count=20`、Hit Rate@K `0.7`、MRR@K `0.475`、Recall@K `0.625`、failure count `0`、fallback count `0`、trace metadata count `62`。
- 依 `.tmp/retrieval-eval-result-keyword.json` 重新產生 `eval-summary.png`。
- `rg -n "frontend-overview.png|frontend-trace.png|eval-summary.png" README.md` 通過。
- `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
