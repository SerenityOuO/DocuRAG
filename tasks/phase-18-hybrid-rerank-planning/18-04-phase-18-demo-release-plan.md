# 18-04 Phase 18 Demo Release Plan

## Goal

規劃 future Phase 18 demo / release checklist，明確定義若後續完成 `hybrid_rerank` implementation，應如何驗證、同步文件與形成 `v0.18.0` release artifact；本 ticket 不執行版本 bump。

## Scope

- 規劃 future validation：backend tests、frontend build、baseline demo smoke、baseline eval smoke、optional vector / `vector_rerank` / `hybrid` / `hybrid_rerank` eval smoke。
- 規劃 future release sync 檔案：backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP。
- 明確記錄 production eval dashboard、Redis、NATS、worker、DB、auth、RBAC 與 deployment 仍留到後續 Phase。
- 只更新 Markdown 規劃文件與 checklist。

## Out of Scope

- 不 bump backend / frontend version，不修改 package lock，不修改 Docker Compose version。
- 不實作 `hybrid_rerank` runtime、eval runner、frontend UI、backend API 或 smoke script。
- 不 push tag、不建立 release note、不建立 GitHub release。
- 不新增外部依賴、DB schema、auth、worker、queue、deployment 或 Docker service。

## Release Impact

- Target version: `v0.18.0` future release sync。
- Version bump required: no。
- 原因：本 ticket 只建立 future release checklist；實際 `v0.18.0` 版本同步必須等後續 implementation ticket 完成並通過 validation 後才可執行。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-18-hybrid-rerank-planning/18-04-phase-18-demo-release-plan.md`

## Acceptance Criteria

- [ ] 已列出 future Phase 18 release sync 檔案與 validation 清單。
- [ ] 已明確寫出這張 ticket 不 bump version。
- [ ] 已保留 production dashboard、infra、DB、auth 與 deployment 到後續 Phase。
- [ ] Release Impact 明確寫 `Version bump required: no` 並說明原因。

## Validation

- `rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no|release sync" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md`
- `git diff --check`
