# Phase 40 Observability Dashboard Evidence

This is interview evidence for the DocuRAG logging and monitoring path. It builds on the Phase 39 opt-in Loki + Grafana baseline and does not claim production alerting, SLO, incident workflow, distributed tracing or APM vendor integration.

## Evidence Map

| Evidence area | Event type | Dashboard / query example | What it demonstrates |
|---|---|---|---|
| API log | `api_request` | API latency p95, API error rate | Request-level health, route errors and p95 latency. |
| Worker log | `worker_log` | Worker task failures | Async task failure visibility with task type and error code. |
| RAG trace | `rag_trace` | RAG retrieval latency, RAG rerank latency, RAG generation latency, fallback count | Retrieval / rerank / generation timing and fallback behavior. |
| Eval metrics | `eval_metrics` | Hit Rate, MRR | Evaluation trend evidence for retrieval quality. |

Primary local assets:

- `infra/observability/README.md`
- `infra/observability/grafana-dashboard-docurag-evidence.json`
- `scripts/observability-smoke.ps1`

## Unavailable / Fallback Behavior

Observability is opt-in. If `DOCURAG_OBSERVABILITY_LOG_PATH` is empty, the app runs without JSONL event export. If Loki, Grafana, Promtail or OpenSearch are unavailable, API requests, RAG queries, eval runs and worker task handling must still continue. If local JSONL write fails, the app logs a warning and does not hard fail the request.

This ticket does not require a live dashboard screenshot. The dashboard JSON skeleton is demo-safe and can be imported into local Grafana when the `observability` Compose profile is available.

## Log Schema Mapping

Every event uses `schema_version=docurag_observability_v1`.

| Field | Required evidence use |
|---|---|
| `trace_id` | Correlates API, RAG trace, eval metrics and worker log events. |
| `request_id` | Ties API log events to request handling. |
| `organization_id` | Shows tenant / org scope when auth context exists. |
| `project_id` | Shows project scope for RAG, eval and worker events. |
| `document_id` | Connects document-scoped ingestion, OCR, parser and indexing work. |
| `strategy` | Names route, retrieval strategy, eval strategy or worker task type. |
| `provider` | Names runtime provider such as `hybrid_rerank`, `keyword`, `nats` or `local_json`. |
| `latency_ms` | Shared latency field for API latency p95 and operational timing panels. |
| `status` | Supports ok / client_error / error / queued / running / succeeded / failed filters. |
| `error_code` | Groups API, worker or provider failures without exposing secrets. |

## Grafana Dashboard Skeleton

Dashboard skeleton: `infra/observability/grafana-dashboard-docurag-evidence.json`.

Panel spec:

| Panel | Event type | LogQL intent |
|---|---|---|
| API latency p95 | `api_request` | `quantile_over_time(0.95, ... unwrap latency_ms ...)` |
| API error rate | `api_request` | error request rate divided by all request rate |
| Worker task failures | `worker_log` | failed task count by `task_type` and `error_code` |
| RAG retrieval latency | `rag_trace` | p95 `retrieval_latency_ms` |
| RAG rerank latency | `rag_trace` | p95 `rerank_latency_ms` |
| RAG generation latency | `rag_trace` | p95 `generation_latency_ms` |
| Fallback count | `rag_trace`, `eval_metrics` | summed `fallback_count` |
| Eval Hit Rate | `eval_metrics` | average `hit_rate_at_k` |
| Eval MRR | `eval_metrics` | average `mrr_at_k` |

## Query Examples

API latency p95:

```logql
quantile_over_time(0.95, {service="docurag", event_type="api_request"} | json | unwrap latency_ms [5m])
```

API error rate:

```logql
sum(rate({service="docurag", event_type="api_request", status!="ok"}[5m]))
/
sum(rate({service="docurag", event_type="api_request"}[5m]))
```

Worker task failures:

```logql
sum by (task_type, error_code) (count_over_time({service="docurag", event_type="worker_log", status="failed"}[15m]))
```

RAG retrieval latency:

```logql
quantile_over_time(0.95, {service="docurag", event_type="rag_trace"} | json | unwrap retrieval_latency_ms [5m])
```

RAG rerank latency:

```logql
quantile_over_time(0.95, {service="docurag", event_type="rag_trace"} | json | unwrap rerank_latency_ms [5m])
```

RAG generation latency:

```logql
quantile_over_time(0.95, {service="docurag", event_type="rag_trace"} | json | unwrap generation_latency_ms [5m])
```

Fallback count:

```logql
sum_over_time({service="docurag", event_type=~"rag_trace|eval_metrics"} | json | unwrap fallback_count [15m])
```

Hit Rate:

```logql
avg_over_time({service="docurag", event_type="eval_metrics"} | json | unwrap hit_rate_at_k [30m])
```

MRR:

```logql
avg_over_time({service="docurag", event_type="eval_metrics"} | json | unwrap mrr_at_k [30m])
```

OpenSearch note: OpenSearch can index the same JSONL fields as saved query / dashboard field mapping. Phase 40 keeps Grafana + Loki as the selected evidence path because Phase 39 already provides the local Compose profile and Promtail labels.

## Demo-Safe Result Template

Use this table when recording a local query result without exposing document text, prompts, bearer tokens or production identifiers.

| Query example | Expected safe result fields | Demo-safe rule |
|---|---|---|
| API latency p95 | route, p95 latency, time window | Do not include request payloads or auth headers. |
| API error rate | route, status, error_code, rate | Do not include bearer tokens or raw exception bodies. |
| Worker task failures | task_type, status, error_code, attempt | Do not include production document content. |
| RAG trace latency | strategy, provider, latency_ms, fallback count | Do not include raw query text, prompt or retrieved document text. |
| Eval metrics | dataset id, Hit Rate, MRR, fallback count | Use demo-safe dataset names only. |

## Validation

```powershell
rg -n "observability evidence|Loki|Grafana|OpenSearch|dashboard|query example|RAG trace|eval metrics|latency|p95|error rate|fallback count|Hit Rate|MRR|trace_id|request_id|error_code" docs infra outputs README_DEV.md TODO.md tasks/phase-40-interview-evidence-hardening
git diff --check
```
