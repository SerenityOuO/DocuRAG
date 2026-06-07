# Worker Demo Smoke and Phase 33 Release Sync

## Goal

完成 Phase 33 `v0.33.0` release sync，讓 Redis + NATS worker pipeline 形成可展示、可驗證的 async architecture milestone。

## Scope

- 補 worker demo smoke script，驗證 Redis、NATS、worker skeleton 與 task status。
- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.33.0`。
- 更新 README、README_DEV、backend / frontend README、TODO 與 ROADMAP。
- 記錄 final validation 與 runtime unavailable fallback。

## Out of Scope

- 不新增 production autoscaling、K8s、distributed tracing 或 full observability stack。
- 不修改 OCR / parser / RAG / Agent model behavior。
- 不新增 vLLM、OpenAI API 或 fine-tuning pipeline。

## Release Impact

- Target version: `v0.33.0`
- Version bump required: yes
- 原因：Phase 33 新增 Redis + NATS worker pipeline demonstration，是 architecture-level release。

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
- `tasks/phase-33-redis-nats-worker-pipeline/33-04-worker-demo-smoke-and-release-sync.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.33.0`。
- [x] Worker smoke 可驗證 Redis / NATS / task status path。
- [x] README 說明 Redis + NATS 是 demo-safe worker pipeline，不是 production autoscaling。
- [x] TODO 與 ROADMAP 記錄 Phase 33 完成狀態與 validation。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Worker demo smoke script。
- `rg -n "v0.33.0|Phase 33|Redis|NATS|worker|task status|JetStream" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend infra scripts tasks/phase-33-redis-nats-worker-pipeline`
- `git diff --check`

## Validation Result

- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`（`227 passed`，1 pytest cache warning）。
- Passed: `npm.cmd run build`。
- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\worker-demo-smoke.ps1`（health version `0.33.0`，Redis fake-client path `ok`，NATS memory worker 與 task status `succeeded`）。
- Passed: `rg -n "v0.33.0|Phase 33|Redis|NATS|worker|task status|JetStream" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend infra scripts tasks/phase-33-redis-nats-worker-pipeline`。
- Passed: `git diff --check`（僅 Windows LF/CRLF 提示）。
