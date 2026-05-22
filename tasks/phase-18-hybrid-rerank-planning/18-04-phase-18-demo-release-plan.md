# 18-04 Phase 18 Demo Release Plan

## Goal

規劃 future `hybrid_rerank` demo / release checklist，明確定義若後續完成 implementation，應如何驗證、同步文件與形成 release artifact；本 ticket 不執行版本 bump。後續 implementation 已排入 Phase 19 / `v0.19.0`。

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

- Target version: `v0.18.0` planning backlog；implementation release target is now `v0.19.0`。
- Version bump required: no。
- 原因：本 ticket 只建立 future release checklist；實際 `v0.19.0` 版本同步必須等 Phase 19 implementation ticket 完成並通過 validation 後才可執行。

## Future Validation Checklist

若後續 implementation ticket 完成 `hybrid_rerank` runtime / eval integration，release sync 前至少需完成：

- backend tests：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- frontend build：`npm.cmd run build`（於 `frontend/`）
- baseline demo smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- baseline eval smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- optional vector eval smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVector`
- optional `vector_rerank` eval smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVectorRerank`
- optional `hybrid` eval smoke：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybrid`
- future optional `hybrid_rerank` eval smoke：只在後續 ticket 明確新增 flag 後執行，且必須保留 baseline fallback。
- `git diff --check`

Optional smoke 若需要 Ollama embedding、Qdrant collection 或 rerank runtime，必須在 validation notes 清楚記錄 preflight 狀態、fallback count 與 fallback reasons。

## Future Release Sync Files

若後續 implementation 形成 `v0.19.0` release artifact，release sync ticket 應同步檢查：

- backend version
- frontend `package.json` version
- frontend package lock version（若 package version changed）
- frontend fallback version
- health test expected version
- Docker Compose `DOCURAG_VERSION`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

本 ticket 不修改上述版本檔；只固定後續 release sync checklist。

## Deferred Items

以下項目仍留到後續 Phase，不應隨 `hybrid_rerank` release sync 一起偷渡：

- production eval dashboard、strategy comparison page、export UI 或 live eval runner
- Redis、NATS、worker、async queue
- PostgreSQL schema、登入、RBAC、tenant / project auth
- deployment 設定、K8s manifests、release tag 或 GitHub release
- LLM-as-judge、answer faithfulness、citation quality scoring、query rewriting 或 BM25 dependency

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-18-hybrid-rerank-planning/18-04-phase-18-demo-release-plan.md`

## Acceptance Criteria

- [x] 已列出 future Phase 18 release sync 檔案與 validation 清單。
- [x] 已明確寫出這張 ticket 不 bump version。
- [x] 已保留 production dashboard、infra、DB、auth 與 deployment 到後續 Phase。
- [x] Release Impact 明確寫 `Version bump required: no` 並說明原因。

## Validation

- `rg -n "v0.18.0|Phase 18|hybrid_rerank|Version bump required: no|release sync" TODO.md docs/ROADMAP.md tasks/phase-18-hybrid-rerank-planning/*.md`
- `git diff --check`
