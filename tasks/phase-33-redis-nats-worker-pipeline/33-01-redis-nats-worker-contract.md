# Redis NATS Worker Contract

## Goal

定義 Phase 33 Redis + NATS worker pipeline 的最小架構合約，避免直接把 queue、cache、worker 與 model runtime 混在一起。

## Scope

- 定義 Redis 用途：session cache、query cache、rate limit、worker lock、short-term chat history。
- 定義 NATS / JetStream topics：document uploaded、OCR requested、parser requested、index requested、eval requested。
- 定義 task status schema、retry policy、failure reason 與 idempotency key。
- 更新 architecture、ROADMAP、TODO 與 README_DEV 的 Phase 33 邊界。

## Out of Scope

- 不新增 Redis / NATS runtime service 或 worker code。
- 不修改 OCR、parser、RAG、eval 或 Agent 實際執行行為。
- 不新增 production autoscaling、K8s、observability stack 或 deployment 設定。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 33 contract ticket，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-33-redis-nats-worker-pipeline/33-01-redis-nats-worker-contract.md`

## Acceptance Criteria

- [ ] 文件列出 Redis responsibilities 與不可濫用的邊界。
- [ ] 文件列出 NATS topics、payload contract 與 retry / failure policy。
- [ ] task status lifecycle 與 idempotency key 明確。
- [ ] 明確標示本 ticket 不新增 runtime service 或 worker code。

## Validation

- `rg -n "Redis|NATS|JetStream|worker|task status|idempotency|Phase 33" docs README_DEV.md TODO.md tasks/phase-33-redis-nats-worker-pipeline`
- `git diff --check`
