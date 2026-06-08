# Phase 40 Release Sync

## Goal

完成 Phase 40 `v0.40.0` release sync，將 JD evidence hardening 的三個 artifacts 整理成可展示、可驗證的面試補強 milestone。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.40.0`。
- 更新 README、README_DEV、backend / frontend README、TODO 與 ROADMAP。
- 整理 Embedding / SFT evidence、Inference hardware benchmark evidence、Observability dashboard evidence 的 final validation。
- 明確標示 Phase 40 是 evidence hardening，不是新增 production runtime 或 production guarantee。

## Out of Scope

- 不新增 production training pipeline、production inference gateway、multi-GPU serving、production alerting 或 incident workflow。
- 不新增 release tag，除非使用者或 ticket 明確指定。
- 不修改 OCR / parser / RAG / Agent / inference core behavior，除非前置 Phase 40 ticket 明確要求。

## Release Impact

- Target version: `v0.40.0`
- Version bump required: yes
- 原因：Phase 40 完成面試證據補強，是對外展示敘事與 release 文件都會更新的 milestone。

## Files likely to change

- `backend/`
- `frontend/`
- `infra/`
- `docs/`
- `scripts/`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `tasks/phase-40-interview-evidence-hardening/40-05-phase-40-release-sync.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.40.0`。
- [x] README / README_DEV 清楚整理 Phase 40 三個 JD evidence artifacts。
- [x] Embedding / SFT、Inference hardware benchmark、Observability dashboard evidence 都有 validation 紀錄。
- [x] 文件不宣稱 production training、production inference autoscaling 或 production alerting 已完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Phase 40 evidence `rg` validation。
- `rg -n "v0.40.0|Phase 40|JD evidence|SFT|Embedding|KV cache|TOPS|observability|dashboard evidence|production guarantee" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend infra docs scripts tasks/phase-40-interview-evidence-hardening`
- `git diff --check`

## Status

- 已完成 `v0.40.0` release sync。backend package / app version、frontend package / lock / fallback version、frontend fallback label、health test、Docker Compose `DOCURAG_VERSION`、`.env.example`、K8s sample image tag、demo smoke expected version、README、README_DEV、backend README、frontend README、TODO 與 ROADMAP 已同步。
- Phase 40 三份 JD evidence artifacts 已收束：Embedding / SFT experiment evidence、inference hardware benchmark evidence（KV cache / TOPS / provider skip reason）與 observability dashboard evidence。
- Validation passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`260 passed, 1 warning`，pytest cache permission warning）；`npm.cmd run build`；`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`（health `0.40.0`，local Qdrant unavailable fallback 符合預期）；Phase 40 evidence `rg`；release `rg`；`git diff --check`（只有 LF/CRLF 提示）。
- Release Impact：Version bump required: yes。Phase 40 已完成 `v0.40.0` JD evidence hardening release；不新增 production training、production inference autoscaling、production alerting / incident workflow 或 production guarantee。
