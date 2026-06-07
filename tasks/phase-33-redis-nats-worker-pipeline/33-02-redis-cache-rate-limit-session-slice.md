# Redis Cache Rate Limit Session Slice

## Goal

新增 Redis 的最小可驗證切片，支援 session cache、query cache 與 rate limit，並保留 Redis unavailable fallback。

## Scope

- 新增 Redis client configuration 與 health helper。
- 實作 demo-safe session cache / query cache / rate limit 的最小 backend slice。
- Redis 不可用時保留清楚 fallback，不讓既有 demo hard fail。
- 補 backend tests 與 smoke validation。

## Out of Scope

- 不新增 NATS、worker、async job queue 或 distributed lock runtime。
- 不新增 production-grade session rotation、OAuth、MFA 或 enterprise auth。
- 不修改 OCR、parser、RAG ranking 或 Agent planner。

## Release Impact

- Target version: `v0.33.0`
- Version bump required: no
- 原因：這是 Phase 33 runtime ticket，版本同步留到 `33-04`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `.env.example`
- `infra/docker-compose.yml`
- `docs/architecture.md`
- `TODO.md`
- `tasks/phase-33-redis-nats-worker-pipeline/33-02-redis-cache-rate-limit-session-slice.md`

## Acceptance Criteria

- [ ] Redis client 可透過 env 設定，並有 unavailable fallback。
- [ ] Rate limit / cache 行為有 backend tests。
- [ ] Docker Compose 可選啟動 Redis service。
- [ ] 文件說明 Redis slice 不等於 worker pipeline 完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- Redis smoke script 或手動 health check。
- `rg -n "Redis|rate limit|query cache|session cache|fallback" backend docs infra TODO.md tasks/phase-33-redis-nats-worker-pipeline`
- `git diff --check`
