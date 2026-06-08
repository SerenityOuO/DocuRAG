# Observability Dashboard Evidence

## Goal

建立 observability dashboard / query examples / screenshots 的面試證據，讓 Phase 39 的 Loki / Grafana 或 OpenSearch path 不只停留在架構文字。

## Scope

- 新增 observability evidence docs，包含 API log、worker log、RAG trace、retrieval latency、rerank latency、generation latency、eval metrics 的 dashboard / query examples。
- 若有 local dashboard，可保存 demo-safe screenshot 或 query result 範例。
- 補充 fallback / unavailable behavior，讓 observability stack 沒啟動時 app 仍可運作。
- 將 evidence 對齊 JD 中 ELK / Loki / logging system 與 ops monitoring 能力。
- Query examples 至少覆蓋 API error rate、API latency p95、worker task failures、RAG retrieval latency、rerank latency、generation latency、fallback count 與 eval Hit Rate / MRR。
- 若選 Grafana，至少提供 dashboard JSON skeleton 或 panel spec；若選 OpenSearch，至少提供 saved query / dashboard field mapping。
- Evidence docs 必須包含 log schema mapping：trace_id、request_id、organization_id、project_id、document_id、strategy、provider、latency_ms、status 與 error_code。

## Out of Scope

- 不新增 production alerting、SLO、incident workflow、distributed tracing 或 APM vendor integration。
- 不要求啟動完整 ELK / Loki stack 才能通過 baseline demo。
- 不修改 RAG ranking、Agent planner、OCR / parser behavior 或 worker runtime。
- 不新增大量 binary media；若需要截圖，使用 demo-safe 小檔並更新 README_DEV 說明。

## Release Impact

- Target version: `v0.40.0`
- Version bump required: no
- 原因：這是 Phase 40 evidence artifact ticket，版本同步留到 `40-05`。

## Files likely to change

- `docs/`
- `infra/`
- `outputs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-40-interview-evidence-hardening/40-04-observability-dashboard-evidence.md`

## Acceptance Criteria

- [x] 有一份 observability evidence docs，包含 dashboard / query examples。
- [x] Evidence 覆蓋 API log、worker log、RAG trace、latency 與 eval metrics。
- [x] Query examples 覆蓋 API latency p95、error rate、worker task failures、retrieval / rerank / generation latency、fallback count、Hit Rate 與 MRR。
- [x] Dashboard evidence 至少包含 Grafana dashboard JSON skeleton、panel spec、OpenSearch saved query 或 demo-safe screenshot 其中一種。
- [x] Log schema mapping 包含 trace_id、request_id、project_id、strategy、provider、latency_ms、status 與 error_code。
- [x] 若有截圖或 query result，必須是 demo-safe 且可在 README_DEV 找到說明。
- [x] 文件明確標示這是 observability evidence，不是 production alerting stack。
- [x] App 在 observability stack unavailable 時仍有 fallback / skip 說明。

## Validation

- `rg -n "observability evidence|Loki|Grafana|OpenSearch|dashboard|query example|RAG trace|eval metrics|latency|p95|error rate|fallback count|Hit Rate|MRR|trace_id|request_id|error_code" docs infra outputs README_DEV.md TODO.md tasks/phase-40-interview-evidence-hardening`
- `git diff --check`

## Status

- Completed. Added `docs/observability-dashboard-evidence.md`.
- Added `infra/observability/grafana-dashboard-docurag-evidence.json` as a demo-safe Grafana dashboard JSON skeleton.
- Updated `infra/observability/README.md`, `README_DEV.md`, `TODO.md` and `docs/ROADMAP.md`.
- Evidence covers API log, worker log, RAG trace, eval metrics, API latency p95, API error rate, worker task failures, retrieval / rerank / generation latency, fallback count, Hit Rate, MRR and log schema mapping.
- Release Impact: Version bump required: no. Version sync remains deferred to `40-05`.
- Validation passed: ticket `rg`, Grafana dashboard JSON parse and `git diff --check`.
