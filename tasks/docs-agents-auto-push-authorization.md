# AGENTS Auto Push Authorization

## Goal

更新 `AGENTS.md` 的 Git 自動上傳規範，明確記錄使用者授權：完成每張 ticket 或明確指定任務後，Codex 可在完成 validation、只 stage 本次相關檔案並建立 commit 後，自動 push 到目前分支的遠端 upstream。

## Scope

- 在 `AGENTS.md` 的 Git 自動上傳規範中補上使用者對自動 remote push 的專案預設授權。
- 明確保留安全邊界：不 force push、不推 tag、不 stage 無關檔案、不繞過系統或工具安全審核。
- 更新 `TODO.md` 的 documentation maintenance checklist。

## Out of Scope

- 不修改 backend、frontend、scripts、sample data、infra 或 runtime 行為。
- 不更新 backend / frontend version、Docker Compose `DOCURAG_VERSION` 或 release artifact。
- 不新增 GitHub Actions、branch protection、deploy key、token、credential 或 CI/CD 設定。
- 不推 tag，不 force push，不變更遠端 repository 設定。
- 不新增外部依賴、資料庫 schema、登入、權限、worker、Redis、NATS、Qdrant、OCR、RAG、vLLM 或 deployment 能力。

## Release Impact

- Target version: none.
- Version bump required: no.
- 原因：本 ticket 只更新 Codex 操作規範與 TODO 紀錄，不改 runtime、API、版本或 release artifact。

## Files likely to change

- `AGENTS.md`
- `TODO.md`
- `tasks/docs-agents-auto-push-authorization.md`

## Acceptance Criteria

- [x] `AGENTS.md` 明確說明使用者授權完成 ticket 後自動 push 目前分支 upstream。
- [x] `AGENTS.md` 保留不 force push、不推未指定 tag、不 stage 無關檔案的限制。
- [x] `AGENTS.md` 明確說明系統、工具或安全審核要求 approval / 拒絕時，以審核結果為準，不得繞過。
- [x] `TODO.md` 有對應 documentation maintenance 紀錄。
- [x] 本 ticket 不修改任何程式碼或 runtime 設定。

## Validation

- `rg -n "自動 push|自動上傳|授權|force push|安全審核|upstream" AGENTS.md TODO.md tasks/docs-agents-auto-push-authorization.md`
- `git diff --check`

Validation result：

- [x] `rg -n "自動 push|自動上傳|授權|force push|安全審核|upstream" AGENTS.md TODO.md tasks/docs-agents-auto-push-authorization.md` 通過。
- [x] `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
