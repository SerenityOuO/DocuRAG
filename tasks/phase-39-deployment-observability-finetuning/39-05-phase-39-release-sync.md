# Phase 39 Release Sync

## Goal

完成 Phase 39 `v0.39.0` release sync，將 deployment baseline、observability path 與 fine-tuning research track 整理成最終 enterprise completion milestone。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.39.0`。
- 更新 README、README_DEV、backend / frontend README、TODO 與 ROADMAP。
- 執行 backend tests、frontend build、baseline demo smoke、K8s validation、observability validation 與 research artifact validation。
- 明確記錄 limitation：不是 production autoscaling、multi-cluster deployment 或 production training pipeline。

## Out of Scope

- 不新增 production autoscaling、enterprise SSO、multi-cluster deployment、managed secret integration 或 production model training。
- 不新增 release tag，除非使用者或 ticket 明確指定。
- 不修改 OCR / parser / RAG / Agent / inference core behavior，除非前置 Phase 39 ticket 明確要求。

## Release Impact

- Target version: `v0.39.0`
- Version bump required: yes
- 原因：Phase 39 完成 deployment / observability / research track 的 final release sync。

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
- `tasks/phase-39-deployment-observability-finetuning/39-05-phase-39-release-sync.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.39.0`。
- [x] README / README_DEV 整理 Phase 31-39 enterprise completion 狀態。
- [x] K8s / observability / research artifact validation 有紀錄。
- [x] 文件不宣稱 production autoscaling 或 production training pipeline 已完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- K8s manifest validation。
- Observability validation。
- Research artifact `rg` validation。
- `rg -n "v0.39.0|Phase 39|K8s|observability|Loki|Grafana|OpenSearch|fine-tuning|synthetic data|production autoscaling" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend infra docs scripts tasks/phase-39-deployment-observability-finetuning`
- `git diff --check`

## Status

- Completed. Phase 39 is released as `v0.39.0`.
- Synchronized backend package / app version, frontend package / lock / fallback version, health test, Docker Compose `DOCURAG_VERSION`, `.env.example`, K8s sample image tag, README, README_DEV, backend README, frontend README, TODO, ROADMAP, demo smoke expected version and this ticket.
- Release boundary remains explicit: this ticket does not add production autoscaling, multi-cluster deployment, managed secret integration, production alerting / incident workflow or production training pipeline.

## Validation Result

- Passed: backend full test `260 passed, 1 warning`（pytest cache permission warning）; frontend build; baseline demo smoke（health `0.39.0`，local Qdrant unavailable keyword fallback matched expected baseline）; K8s offline YAML lint `15 documents`; observability smoke `5 passed, 1 warning`; Docker Compose observability profile config（Docker config permission warning, config parsed successfully）; research artifact `rg`; JSONL parse sanity check; release `rg`; `git diff --check`.
- Attempted: `kubectl apply --dry-run=client --validate=false -f .\infra\k8s`; local machine has no Kubernetes API context, so kubectl failed during API discovery against `localhost:8080`.
