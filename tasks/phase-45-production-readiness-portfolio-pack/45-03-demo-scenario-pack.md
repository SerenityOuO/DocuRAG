# Demo Scenario Pack

## Goal

整理最終面試 demo scenario pack，提供 RAG、Document AI、AgentOps、Inference Ops 與 Observability 的分段展示腳本。

## Scope

- 新增 demo scenario pack 文件。
- 至少包含三條主線：RAG quality、Document Intelligence QA、AgentOps governance。
- 補充 optional path：Inference Gateway / capacity planning、Observability evidence、K8s / deployment boundary。
- 每條 demo path 都列出前置條件、操作步驟、預期畫面 / 輸出與 fallback 解讀。

## Out of Scope

- 不新增新的 demo runtime、sample secrets、外部服務帳號或 paid API。
- 不新增大檔案影片；如需媒體，另開 demo media ticket。
- 不把 optional runtime unavailable 寫成錯誤。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 45 demo documentation ticket，版本同步留到 `45-05`。

## Files likely to change

- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-45-production-readiness-portfolio-pack/45-03-demo-scenario-pack.md`

## Acceptance Criteria

- [x] Demo pack 至少包含 RAG quality、Document Intelligence QA 與 AgentOps governance 三條主線。
- [x] 每條主線包含前置條件、操作步驟、預期結果與 fallback 解讀。
- [x] Optional inference / observability / K8s path 不要求 production runtime。

## Completion Notes

- 新增 `docs/demo-scenario-pack.md`，整理 RAG quality、Document Intelligence QA、AgentOps governance 三條主線。
- 補充 Inference Gateway / capacity planning、Observability evidence、K8s / deployment boundary optional path，並明確標示 optional runtime unavailable 是 skip-safe / fallback，不是錯誤。
- 未新增 demo runtime、sample secrets、外部服務帳號、paid API、optional runtime requirement、影片媒體或 version bump。

## Validation

- `rg -n "demo scenario|RAG quality|Document Intelligence QA|AgentOps governance|Inference Gateway|Observability|fallback" docs README_DEV.md TODO.md tasks/phase-45-production-readiness-portfolio-pack`
- `git diff --check`
