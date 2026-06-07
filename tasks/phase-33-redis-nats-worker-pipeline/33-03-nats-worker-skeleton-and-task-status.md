# NATS Worker Skeleton and Task Status

## Goal

新增 NATS / JetStream worker skeleton 與 task status 回寫，讓 ingestion / eval jobs 可以從同步 API path 拆出可展示的 async pipeline。

## Scope

- 新增 NATS client configuration 與 publish / subscribe helper。
- 建立 worker skeleton，支援 OCR、parser、indexing、eval topic 的 placeholder handler。
- 實作 task status record / update，包含 queued、running、succeeded、failed、retrying。
- 補 backend / worker tests 或 smoke script，驗證 publish、consume 與 status update。

## Out of Scope

- 不改 OCR / parser / indexing / eval 的核心 model 行為。
- 不新增 production autoscaling、K8s、dead-letter dashboard 或 full observability stack。
- 不新增 vLLM、OpenAI API、fine-tuning 或 Agent planner 變更。

## Release Impact

- Target version: `v0.33.0`
- Version bump required: no
- 原因：這是 Phase 33 runtime ticket，版本同步留到 `33-04`。

## Files likely to change

- `backend/app/`
- `backend/workers/`
- `backend/tests/`
- `scripts/`
- `.env.example`
- `infra/docker-compose.yml`
- `docs/architecture.md`
- `TODO.md`
- `tasks/phase-33-redis-nats-worker-pipeline/33-03-nats-worker-skeleton-and-task-status.md`

## Acceptance Criteria

- [ ] NATS publish / consume helper 可被 smoke 驗證。
- [ ] Worker skeleton 能處理至少一個 demo topic 並回寫 task status。
- [ ] Task status API 或 metadata 可顯示 queued / running / succeeded / failed。
- [ ] Runtime unavailable 時有清楚 fallback 或 skip 訊息。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- NATS worker smoke script。
- `rg -n "NATS|JetStream|worker|task status|document.ocr.requested|document.index.requested" backend scripts docs infra TODO.md tasks/phase-33-redis-nats-worker-pipeline`
- `git diff --check`
