# Indexing Quality Demo and Phase 35 Release Sync

## Goal

完成 Phase 35 `v0.35.0` release sync，將 chunking strategy、Qdrant payload index、reindex 與 stale vector cleanup 形成可展示的 RAG indexing quality milestone。

## Scope

- 補 indexing quality demo smoke，驗證 chunking strategy、reindex、metadata filter 與 stale cleanup。
- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.35.0`。
- 更新 README、README_DEV、backend / frontend README、TODO 與 ROADMAP。
- 記錄 validation 與 limitation：不是 production eval dashboard 或 LLM-as-judge。

## Out of Scope

- 不新增 eval dashboard、LLM-as-judge、answer faithfulness 或 citation quality scoring。
- 不更換 default embedding / rerank model，除非另有 ticket。
- 不修改 OCR / parser / Agent planner。

## Release Impact

- Target version: `v0.35.0`
- Version bump required: yes
- 原因：Phase 35 完成 RAG indexing quality user-facing / engineering release。

## Files likely to change

- `backend/`
- `frontend/`
- `scripts/`
- `infra/docker-compose.yml`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `tasks/phase-35-rag-indexing-quality/35-04-indexing-quality-demo-release-sync.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.35.0`。
- [x] Demo smoke 可驗證 chunking strategy 與 reindex / cleanup path。
- [x] README / README_DEV 清楚說明 Phase 35 是 indexing quality，不是 eval dashboard。
- [x] TODO / ROADMAP 記錄 Phase 35 final validation。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Indexing quality smoke script。
- `rg -n "v0.35.0|Phase 35|chunking|Qdrant payload|reindex|stale vector|indexing quality" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend scripts tasks/phase-35-rag-indexing-quality`
- `git diff --check`

## Completion Notes

- Backend package / app version、frontend package / lock / fallback version、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、README、README_DEV、backend README、frontend README、TODO 與 ROADMAP 已同步到 `0.35.0` / `v0.35.0`。
- 新增 `scripts/indexing-quality-smoke.ps1`，以重點 pytest 覆蓋 chunking strategy、Qdrant payload filter、project reindex 與 stale cleanup path。
- Phase 35 release boundary 已明確保留：這是 indexing quality hardening，不是 production eval dashboard、LLM-as-judge、rerank tuning 或 production indexing worker。
- Validation 已執行：backend test script（`240 passed`，1 pytest cache warning）、frontend build、indexing quality smoke（`7 passed`，1 pytest cache warning）、ticket `rg` 與 `git diff --check`。
