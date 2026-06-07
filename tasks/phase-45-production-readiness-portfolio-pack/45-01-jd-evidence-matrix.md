# JD Evidence Matrix

## Goal

建立 JD 條目到 DocuRAG 專案證據的對照表，讓面試官可以快速看到每個能力如何被文件、demo、測試或截圖驗證。

## Scope

- 新增 JD evidence matrix 文件。
- 對照 AI Core、Software / System Architecture、Inference & Ops 三大類能力。
- 每列至少包含 JD keyword、專案證據、demo path、validation command、目前邊界與下一步。
- 標示哪些能力是 completed、demo-safe、research-only 或 future backlog。

## Out of Scope

- 不新增 runtime、dependency、測試程式、截圖或 demo media，除非只是引用既有 artifacts。
- 不誇大 production readiness，不把未完成 roadmap 寫成已完成。
- 不修改 backend / frontend version。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 45 portfolio artifact ticket，版本同步留到 `45-05`。

## Files likely to change

- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-45-production-readiness-portfolio-pack/45-01-jd-evidence-matrix.md`

## Acceptance Criteria

- [ ] JD evidence matrix 覆蓋 AI Core、System Architecture、Inference & Ops。
- [ ] 每列包含 project evidence、demo / validation path 與 honesty boundary。
- [ ] 文件清楚區分 completed、demo-safe、research-only 與 future backlog。

## Validation

- `rg -n "JD evidence matrix|AI Core|System Architecture|Inference|completed|demo-safe|research-only|future backlog" docs README_DEV.md TODO.md tasks/phase-45-production-readiness-portfolio-pack`
- `git diff --check`
