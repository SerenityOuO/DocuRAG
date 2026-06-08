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

- [x] Walkthrough 可在 10 分鐘內說清楚系統資料流與能力邊界。
- [x] 文件包含 failure / fallback 解讀與主要 tradeoffs。
- [x] 文件不誇大 production readiness。

## Validation

- `rg -n "system design walkthrough|Viewer Chat|Admin Ingestion|Redis|NATS|PostgreSQL|inference gateway|observability|tradeoff|fallback" docs README_DEV.md TODO.md tasks/phase-45-production-readiness-portfolio-pack`
- `git diff --check`

## Completion Notes

- Added `docs/system-design-walkthrough.md`.
- Walkthrough includes 10-minute talk track, whiteboard-style data flow, runtime surfaces, failure / fallback reading and main tradeoffs.
- It explicitly frames Redis / NATS, PostgreSQL, inference gateway and observability as demo-safe or opt-in evidence where appropriate, not production readiness.
- No runtime, infra config, deployment service, public README release log or diagram generation tool was added.
