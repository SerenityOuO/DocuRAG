# 20-10 README Chat-First Demo Refresh

## Goal

更新 root README，讓面試展示流程明確對齊 20-09 後的 chat-first frontend：前台先像客服機器人一樣提問，後台才負責文件上傳、OCR、索引與工程追蹤。

## Scope

- 更新 `README.md` 的 demo 說明、推薦啟動順序與前台 / 後台分工描述。
- 明確標示面試前可用 `scripts/seed-demo-data.ps1` 預載公開 synthetic knowledge base。
- 保留 optional Ollama、Qdrant、rerank、hybrid 與 real OCR 說明，但避免讓第一次 demo 看起來必須先跑 real OCR。
- 同步更新本 ticket、`TODO.md` 與 `docs/ROADMAP.md` 的完成狀態。

## Out of Scope

- 不修改 frontend、backend、sample data、eval dataset、smoke script 或 demo media 圖片。
- 不新增 README 圖片路徑、frontend route、backend API endpoint、外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、Agent runtime 或 deployment。
- 不改變 `/rag/query` 預設 keyword baseline，不把 vector、rerank、hybrid 或 `hybrid_rerank` 接到 default frontend chat path。
- 不 bump backend / frontend package version、不更新 Docker Compose `DOCURAG_VERSION`、不新增 release tag。

## Release Impact

- Target version: `v0.20.1` README demo clarification patch。
- Version bump required: no。
- 原因：本 ticket 只更新 README 與追蹤文件，讓文件跟上既有 chat-first demo，不形成新的 runtime release artifact。

## Files likely to change

- `README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-20-interview-mvp-packaging/20-10-readme-chat-first-demo-refresh.md`

## Acceptance Criteria

- [x] README 有清楚的 chat-first recommended demo flow。
- [x] README 說明前台客服聊天與後台知識庫建置的分工。
- [x] README 保留 optional real OCR / LLM / vector / eval 路徑，但不把它們放在 baseline demo 的必要步驟。
- [x] TODO 與 ROADMAP 記錄 20-10 狀態與 validation。

## Validation

- `rg -n "Chat-First|chat-first|客服|後台知識庫|seed-demo-data|20-10" README.md TODO.md docs/ROADMAP.md tasks/phase-20-interview-mvp-packaging/20-10-readme-chat-first-demo-refresh.md`
- `git diff --check`

## Validation Result

- [x] `rg -n "Chat-First|chat-first|客服|後台知識庫|seed-demo-data|20-10" README.md TODO.md docs/ROADMAP.md tasks/phase-20-interview-mvp-packaging/20-10-readme-chat-first-demo-refresh.md` 通過。
- [x] `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
