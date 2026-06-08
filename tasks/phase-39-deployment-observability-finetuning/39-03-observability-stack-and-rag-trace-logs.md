# Observability Stack and RAG Trace Logs

## Goal

新增 observability baseline，集中 API log、worker log、RAG trace 與 eval metrics，讓系統維運能力可被展示。

## Scope

- 選定 Loki / Grafana 或 OpenSearch baseline，新增 local / compose 或 docs path。
- 定義 API log、worker log、RAG trace、retrieval latency、rerank latency、generation latency、eval metrics 的 log schema。
- 新增 sample dashboard / query docs 或 smoke validation。
- 保留 app 在 observability stack unavailable 時可正常運作。
- Log schema 必須保留 trace_id、request_id、organization_id、project_id、actor_user_id、document_id、strategy、provider、latency_ms、status 與 error_code。
- Dashboard / query docs 至少覆蓋 API p95 latency、error rate、worker task failures、retrieval / rerank / generation latency、fallback count、Hit Rate 與 MRR。
- 若新增 local compose path，必須以 profile 或 opt-in 方式啟用，不影響 baseline demo。

## Out of Scope

- 不新增 production alerting、SLO、distributed tracing、APM vendor integration 或 long-term storage。
- 不修改 RAG ranking、Agent planner、OCR / parser behavior。
- 不新增 production incident workflow。

## Release Impact

- Target version: `v0.39.0`
- Version bump required: no
- 原因：這是 Phase 39 observability runtime / docs ticket，版本同步留到 `39-05`。

## Files likely to change

- `backend/app/`
- `backend/tests/`
- `infra/`
- `docs/`
- `scripts/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-39-deployment-observability-finetuning/39-03-observability-stack-and-rag-trace-logs.md`

## Acceptance Criteria

- [x] API / worker / RAG / eval log schema 有明確文件。
- [x] Local observability path 可用 smoke 或 docs 驗證。
- [x] RAG trace 與 eval metrics 可以被集中查詢或匯出。
- [x] Query examples 覆蓋 API p95 latency、error rate、worker failures、RAG latency、fallback count、Hit Rate 與 MRR。
- [x] Observability stack 以 opt-in profile / docs path 啟用，不是 baseline 必要服務。
- [x] Observability stack unavailable 時 app 不 hard fail。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- Observability smoke / query validation。
- `rg -n "Loki|Grafana|OpenSearch|RAG trace|eval metrics|latency|p95|error rate|fallback count|Hit Rate|MRR|trace_id|request_id|log schema|opt-in" backend infra docs scripts README_DEV.md TODO.md tasks/phase-39-deployment-observability-finetuning`
- `git diff --check`

## Status

- Completed. Added `DOCURAG_OBSERVABILITY_LOG_PATH` as an opt-in JSONL exporter setting.
- Added `api_request`, `rag_trace`, `eval_metrics` and `worker_log` events using shared `docurag_observability_v1` fields.
- Added local Loki + Grafana / Promtail path under `infra/observability/` and the `observability` Docker Compose profile.
- Added LogQL query examples for API p95 latency, error rate, worker task failures, retrieval / rerank / generation latency, fallback count, Hit Rate and MRR.
- Added `scripts/observability-smoke.ps1` and focused backend tests.
- Release Impact: Version bump required: no. Version sync remains deferred to `39-05`.

## Validation Result

- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1` (`260 passed, 1 warning`; pytest cache permission warning only).
- Passed: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\observability-smoke.ps1` (`5 passed, 1 warning`; pytest cache permission warning only).
- Passed: `docker-compose -f .\infra\docker-compose.yml --profile observability config`; Docker emitted a local config permission warning for `C:\Users\USER\.docker\config.json`, but Compose config parsing completed successfully.
- Passed: ticket `rg`.
- Passed: `git diff --check`.
