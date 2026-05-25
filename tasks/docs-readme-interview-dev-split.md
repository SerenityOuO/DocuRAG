# README Interview / Dev Split

## Goal

將 root README 切分成兩個入口：

- `README.md`：給面試官、HR 或技術主管快速理解專案價值、目前能力、架構亮點與 demo 路徑。
- `README_DEV.md`：保留原本 root README 的完整開發紀錄、release log、本地啟動細節與 ticket-first 開發備忘。

## Scope

- 將現有 `README.md` 內容搬到 `README_DEV.md`，作為開發紀錄與更新日誌入口。
- 重寫 root `README.md`，聚焦面試官想看的專案簡介、核心能力、技術亮點、架構、demo 與驗證方式。
- 在新 `README.md` 開頭加入直接連到 `README_DEV.md` 的超連結。
- 更新 `TODO.md`，記錄這次 documentation maintenance ticket 已完成。

## Out of Scope

- 不修改 backend、frontend、scripts、sample data、infra 或 runtime 行為。
- 不新增 OCR、RAG、Qdrant、Redis、NATS、vLLM、登入、權限、資料庫 schema、worker 或 deployment 能力。
- 不更新 backend / frontend version、Docker Compose `DOCURAG_VERSION` 或 release artifact。
- 不重寫 `goal.md`、PRD、architecture 或 ROADMAP 的產品規劃。

## Release Impact

- Target version: none.
- Version bump required: no.
- 原因：本 ticket 只調整 root README 的讀者分工與文件入口，不改 runtime、API、版本或 release artifact。

## Files likely to change

- `README.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/docs-readme-interview-dev-split.md`

## Acceptance Criteria

- [x] `README.md` 第一屏有連到 `README_DEV.md` 的超連結。
- [x] `README.md` 以面試官視角說明專案定位、核心能力、技術亮點、demo path 與驗證方式。
- [x] `README_DEV.md` 保留原本 root README 的完整開發紀錄與 release log。
- [x] `TODO.md` 有對應 checklist 紀錄。
- [x] 本 ticket 不修改任何程式碼或 runtime 設定。

## Validation

- `rg -n "README_DEV.md|開發紀錄|面試官|技術亮點|Release Status" README.md README_DEV.md TODO.md tasks/docs-readme-interview-dev-split.md`
- `git diff --check`

Validation result：

- [x] `rg -n "README_DEV.md|開發紀錄|面試官|技術亮點|Release Status" README.md README_DEV.md TODO.md tasks/docs-readme-interview-dev-split.md` 通過。
- [x] `git diff --check` 通過（僅 Windows LF/CRLF 提示）。
