# Risk Boundary and Tradeoff Report

## Goal

建立 risk / boundary / tradeoff report，誠實整理 DocuRAG 已完成、demo-safe、research-only 與 future production hardening 的差異。

## Scope

- 梳理主要風險：資料隔離、production DB migration、worker durability、observability、model latency、OCR / VLM accuracy、Agent tool safety。
- 每個風險列出目前 mitigation、剩餘缺口、下一步 ticket 或 future backlog。
- 補充面試回答用 tradeoff：為什麼保留 fallback、為什麼不提前導入 production service。
- 與 JD evidence matrix 互相引用。

## Out of Scope

- 不新增 runtime safety control、production incident workflow、SLO、pager、external vendor integration。
- 不修改現有功能行為。
- 不把 future hardening 寫成已完成。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 45 portfolio risk report ticket，版本同步留到 `45-05`。

## Files likely to change

- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-45-production-readiness-portfolio-pack/45-04-risk-boundary-and-tradeoff-report.md`

## Acceptance Criteria

- [ ] Report 覆蓋資料隔離、DB migration、worker durability、observability、latency、OCR / VLM accuracy 與 Agent safety。
- [ ] 每個風險都有 mitigation、剩餘缺口與下一步。
- [ ] 文件可作為面試時回答 tradeoff 的材料。

## Validation

- `rg -n "risk boundary|tradeoff|data isolation|migration|worker durability|observability|latency|OCR|VLM|Agent safety|mitigation" docs README_DEV.md TODO.md tasks/phase-45-production-readiness-portfolio-pack`
- `git diff --check`
