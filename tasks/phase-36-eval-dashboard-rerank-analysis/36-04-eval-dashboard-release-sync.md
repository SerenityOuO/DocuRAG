# Eval Dashboard Phase 36 Release Sync

## Goal

完成 Phase 36 `v0.36.0` release sync，將 eval dashboard / rerank analysis 形成可展示 release。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.36.0`。
- 更新 README、README_DEV、backend / frontend README、TODO 與 ROADMAP。
- 執行 backend tests、frontend build、eval dashboard smoke 與 Browser validation。
- 記錄 limitation：不包含 LLM-as-judge、answer faithfulness 或 citation quality scoring。

## Out of Scope

- 不新增 LLM-as-judge、answer faithfulness、citation quality scoring 或 OCR eval。
- 不新增 production monitoring trend、alerting 或 observability stack。
- 不修改 inference provider 或 Agent runtime。

## Release Impact

- Target version: `v0.36.0`
- Version bump required: yes
- 原因：Phase 36 完成可操作 eval dashboard，是明確 user-facing release。

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
- `tasks/phase-36-eval-dashboard-rerank-analysis/36-04-eval-dashboard-release-sync.md`

## Acceptance Criteria

- [ ] `/health` 回傳 `0.36.0`。
- [ ] README / README_DEV 說明 eval dashboard 能力與明確限制。
- [ ] Final validation 包含 dashboard smoke 與 Browser desktop / mobile check。
- [ ] TODO / ROADMAP 記錄 Phase 36 完成狀態。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Eval dashboard smoke script。
- Browser 檢查 eval dashboard desktop / mobile。
- `rg -n "v0.36.0|Phase 36|eval dashboard|strategy comparison|rerank analysis|Hit Rate|MRR|Recall" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend scripts tasks/phase-36-eval-dashboard-rerank-analysis`
- `git diff --check`
