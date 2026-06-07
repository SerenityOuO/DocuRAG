# System Design Walkthrough

## Goal

建立一份面試用 system design walkthrough，讓 DocuRAG 的資料流、權限、非同步任務、RAG eval、inference 與 observability 能在 10 分鐘內講清楚。

## Scope

- 新增或更新 system design walkthrough 文件。
- 說明 Viewer Chat、Admin Ingestion、OCR / VLM parser、RAG indexing / eval、AgentOps、Redis / NATS、PostgreSQL、inference gateway 與 observability 的角色。
- 補充主要 tradeoffs：local JSON vs PostgreSQL、sync API vs worker、demo-safe vs production-ready。
- 提供白板式資料流與 failure / fallback 解讀。

## Out of Scope

- 不新增架構圖生成工具、runtime、infra config 或 deployment service。
- 不把 future backlog 寫成已完成。
- 不新增長篇 release log 到 public README。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 45 portfolio documentation ticket，版本同步留到 `45-05`。

## Files likely to change

- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-45-production-readiness-portfolio-pack/45-02-system-design-walkthrough.md`

## Acceptance Criteria

- [ ] Walkthrough 可在 10 分鐘內說清楚系統資料流與能力邊界。
- [ ] 文件包含 failure / fallback 解讀與主要 tradeoffs。
- [ ] 文件不誇大 production readiness。

## Validation

- `rg -n "system design walkthrough|Viewer Chat|Admin Ingestion|Redis|NATS|PostgreSQL|inference gateway|observability|tradeoff|fallback" docs README_DEV.md TODO.md tasks/phase-45-production-readiness-portfolio-pack`
- `git diff --check`
