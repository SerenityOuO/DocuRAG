# Phase 31-39 Roadmap Plan

## Goal

新增 Phase 31 到 Phase 39 的後續完成路線，將目前尚未完成的 enterprise / production 能力拆成可逐步實作的版本化階段，避免後續把 PostgreSQL、RBAC、Redis、NATS、worker、OCR pipeline、eval dashboard、vLLM、K8s 與 fine-tuning 混成單一大 ticket。

## Scope

- 在 `TODO.md` 新增 Phase 31 到 Phase 39 的 target version map 與後續 checklist。
- 在 `docs/ROADMAP.md` 新增 Phase 31 到 Phase 39 的 roadmap section、每階段 goal、expected outcome、guardrails 與 validation direction。
- 在 `README_DEV.md` 補充後續開發方向，說明 Phase 31 到 Phase 39 是 future roadmap，不是目前已完成 release。
- 明確標示本 ticket 僅新增規劃文件，不新增 runtime、依賴、DB schema、worker、deployment 或版本 bump。

## Out of Scope

- 不修改 backend / frontend 程式碼。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、queue、正式 Auth / RBAC、K8s manifest、vLLM runtime、OpenAI SDK、SFT notebook 或 fine-tuning pipeline。
- 不更新 backend package version、frontend package version、frontend fallback version、health test 或 Docker Compose `DOCURAG_VERSION`。
- 不新增 release tag 或 commit tag。
- 不把 Phase 31 到 Phase 39 描述成已完成能力。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：本 ticket 只新增未來 roadmap 與 backlog 規劃，沒有 runtime 行為變更，也沒有完成任何 Phase release。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `tasks/phase-31-enterprise-roadmap/31-01-phase-31-to-39-roadmap-plan.md`

## Acceptance Criteria

- [x] `TODO.md` 包含 Phase 31 到 Phase 39 的 target version map 與 pending checklist。
- [x] `docs/ROADMAP.md` 包含 Phase 31 到 Phase 39 的 goal、expected outcome 與 guardrails。
- [x] `README_DEV.md` 說明 Phase 31 到 Phase 39 是後續方向，不是目前 release status。
- [x] 文件明確保留 ticket-first 原則，後續每個 Phase 仍需拆小 ticket 執行。
- [x] 文件沒有宣稱 PostgreSQL、正式 RBAC、Redis、NATS、worker、vLLM、K8s 或 fine-tuning 已完成。

## Validation

- `rg -n "Phase 31|Phase 39|v0.31.0|v0.39.0|PostgreSQL|Redis|NATS|vLLM|K8s|fine-tuning" TODO.md docs/ROADMAP.md README_DEV.md tasks/phase-31-enterprise-roadmap/31-01-phase-31-to-39-roadmap-plan.md`
- `rg -n "Version bump required: no|Target version: `none`|future roadmap|尚未完成|不新增 runtime" TODO.md docs/ROADMAP.md README_DEV.md tasks/phase-31-enterprise-roadmap/31-01-phase-31-to-39-roadmap-plan.md`
- `git diff --check`

Validation result：

- 第一個 `rg` 通過，確認 Phase 31 到 Phase 39、版本號與 enterprise keywords 已同步。
- 第二個 `rg` 通過；PowerShell 需用單引號避免反引號被解讀成跳脫字元。
- `git diff --check` 通過，僅顯示 Windows LF/CRLF 提示。
