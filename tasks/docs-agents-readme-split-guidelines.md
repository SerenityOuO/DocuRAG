# AGENTS README Split Guidelines

## Goal

更新 `AGENTS.md`，讓後續 Codex ticket 明確遵守 root 雙 README 分工：

- `README.md` 是面試官 / HR / 技術主管看的公開入口。
- `README_DEV.md` 是作者與開發者看的開發紀錄、release log 與本地驗證備忘。

## Scope

- 在 `AGENTS.md` 新增 README 分工規範。
- 更新 ticket 開始前的必讀文件清單，納入 `README_DEV.md`。
- 更新 release sync 規則，讓需要 release 的 Phase 同步考慮 `README.md` 與 `README_DEV.md`。
- 更新 `README.md` / `README_DEV.md` 的 Release Status 規則，避免未來把長篇 release log 寫回面試官入口。
- 更新 `TODO.md` 的 documentation maintenance checklist。

## Out of Scope

- 不修改 backend、frontend、scripts、sample data、infra 或 runtime 行為。
- 不更新 backend / frontend version、Docker Compose `DOCURAG_VERSION` 或 release artifact。
- 不修改 README 內容本身。
- 不新增外部依賴、資料庫 schema、登入、權限、worker、Redis、NATS、Qdrant、OCR、RAG、vLLM 或 deployment 能力。

## Release Impact

- Target version: none.
- Version bump required: no.
- 原因：本 ticket 只更新 Codex 開發規範與 TODO 紀錄，不改 runtime、API、版本或 release artifact。

## Files likely to change

- `AGENTS.md`
- `TODO.md`
- `tasks/docs-agents-readme-split-guidelines.md`

## Acceptance Criteria

- [x] `AGENTS.md` 明確定義 `README.md` 與 `README_DEV.md` 的讀者、內容邊界與更新規則。
- [x] `AGENTS.md` 的 ticket 前置檢查清單包含 `README_DEV.md`。
- [x] `AGENTS.md` 的 release sync 規則包含 `README_DEV.md`，且說明 `README.md` 不放長篇 release log。
- [x] `TODO.md` 有對應 documentation maintenance 紀錄。
- [x] 本 ticket 不修改任何程式碼或 runtime 設定。

## Validation

- `rg -n "README_DEV.md|README 分工|面試官|Release Status|開發紀錄" AGENTS.md TODO.md tasks/docs-agents-readme-split-guidelines.md`
- `git diff --check`

Validation result：

- [x] `rg -n "README_DEV.md|README 分工|面試官|Release Status|開發紀錄" AGENTS.md TODO.md tasks/docs-agents-readme-split-guidelines.md` 通過。
- [x] `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
