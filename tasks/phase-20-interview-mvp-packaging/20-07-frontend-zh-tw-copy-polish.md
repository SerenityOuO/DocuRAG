# 20-07 Frontend Zh-TW Copy Polish

## Goal

將既有 frontend demo 網頁中可控的可見英文文案改為繁體中文，讓面試展示時 UI 語言更一致。

## Scope

- 只調整既有 Vue single-page UI 的靜態文案、按鈕文字、表格欄位、狀態顯示與瀏覽器標題。
- 保留 API endpoint、JSON key、模型名稱、provider 名稱、檔名與必要技術 token 的原文。
- 增加不改 API contract 的狀態顯示 helper，讓 backend 回傳值在 UI 上可用繁中呈現。
- 同步更新本 ticket、`TODO.md` 與 `docs/ROADMAP.md` 的完成狀態。

## Out of Scope

- 不新增 i18n framework、多語系切換、route、API、外部依賴或 backend runtime。
- 不修改 API response contract、retrieval algorithm、eval runner、smoke script、sample data 或 backend service。
- 不新增 production eval dashboard、strategy comparison page、live eval runner、DB、auth、Redis、NATS、worker、Agent runtime 或 deployment。

## Release Impact

- Target version: `v0.20.1` frontend copy polish patch。
- Version bump required: no。
- 原因：本 ticket 只改善 frontend demo 的中文可讀性，不形成新的 runtime release artifact；不更新 backend / frontend package version 或 Docker Compose `DOCURAG_VERSION`。

## Files likely to change

- `frontend/index.html`
- `frontend/src/App.vue`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] 首頁 hero、summary cards、workflow、panel heading、buttons、table headers、empty states 與 error fallback 文案改為繁體中文。
- [x] 文件狀態、request state 與 latest job 等常見 backend value 在 UI 上能顯示繁中語意。
- [x] API endpoint、JSON key、provider/model 名稱與檔名仍保留原文，不影響面試技術說明。
- [x] 不新增 route、API、外部依賴或 out-of-scope runtime。

## Validation

- `npm.cmd run build`（於 `frontend/`）
- Browser 檢查 local frontend demo view，確認主要可見 UI 文案已中文化且 desktop viewport 無明顯重疊。
- `rg -n "Backend health|Upload document|Upload result|Documents|OCR result|RAG chat|Retrieval trace|Citations|Retrieved chunks|Refresh health|Upload to backend|Ask RAG|No document selected|No job yet" frontend/src/App.vue frontend/index.html`
- `git diff --check`

## Validation Result

- [x] `npm.cmd run build` 於 `frontend/` 通過。
- [x] Local frontend demo view 檢查通過：頁面標題為 `DocuRAG AgentOps 文件智能平台`，主要 panel 顯示中文，舊英文可見標籤未出現在 rendered text，desktop viewport 無 horizontal overflow。
- [x] `rg` 已執行；剩餘命中僅 `listDocuments` / `refreshDocuments` 程式識別符，非可見 UI 文案。
- [x] `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
