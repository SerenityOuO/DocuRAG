# 00-02 - Project Docs

## Goal

整理 Phase 00 的專案文件，讓後續 ticket 能依照 PRD、MVP architecture 與 roadmap 開發。

## Scope

- 檢查並更新 README、PRD、ARCHITECTURE、ROADMAP 與 TODO。
- 確認 docs 只描述 MVP 與近期 phase，不過度設計。
- 確認 ticket 內容與 roadmap 順序一致。

## Out of Scope

- 不新增或修改程式碼。
- 不新增 backend、frontend 或 infra 實作。
- 不安裝套件。
- 不補完整 API spec、DB schema 或 production deployment 文件。

## Files likely to change

- `README.md`
- `TODO.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `tasks/_TEMPLATE.md`
- `tasks/phase-00-bootstrap/*.md`

## Acceptance Criteria

- [ ] README 說明專案目標、MVP 範圍與開發方向。
- [ ] PRD 依 `goal.md` 收斂成目前可執行的產品需求。
- [ ] ARCHITECTURE 只描述 MVP 架構與延後元件。
- [ ] ROADMAP 只列出 Phase 00、Phase 01、Phase 02。
- [ ] TODO 與 tasks 狀態一致。

## Validation

- 人工檢查所有文件章節是否存在。
- 檢查 `git diff --stat` 只包含 Markdown。
