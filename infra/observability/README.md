# DocuRAG Observability Baseline

This folder defines the Phase 39 opt-in Loki + Grafana path for local evidence. It is a demo baseline, not production alerting, SLO management, APM, distributed tracing or long-term log storage.

## Event Export

Backend observability is disabled by default. To export JSONL events, set:

```powershell
$env:DOCURAG_OBSERVABILITY_LOG_PATH = ".tmp/observability/docurag-observability.jsonl"
```

Docker Compose profile usage:

```powershell
$env:DOCURAG_OBSERVABILITY_LOG_PATH = "/app/data/observability/docurag-observability.jsonl"
docker compose -f .\infra\docker-compose.yml --profile observability up backend loki promtail grafana
```

If your Docker installation uses the legacy Compose binary:

```powershell
$env:DOCURAG_OBSERVABILITY_LOG_PATH = "/app/data/observability/docurag-observability.jsonl"
docker-compose -f .\infra\docker-compose.yml --profile observability up backend loki promtail grafana
```

The app keeps running if `DOCURAG_OBSERVABILITY_LOG_PATH` is empty, if Loki / Grafana / Promtail are down, or if the JSONL file cannot be written. Failed local writes are logged as warnings and do not fail API requests.

## Log Schema

Every exported event uses `schema_version=docurag_observability_v1` and keeps these shared fields:

| Field | Meaning |
|---|---|
| `trace_id` | Request or task trace id. |
| `request_id` | API request id when available. |
| `organization_id` | Organization scope, if auth context provides it. |
| `project_id` | Active project scope, if auth context provides it. |
| `actor_user_id` | Authenticated username, if available. |
| `document_id` | First affected document id, if applicable. |
| `strategy` | API route strategy, RAG strategy, eval strategy or worker task type. |
| `provider` | Runtime provider such as `keyword`, `hybrid_rerank`, `nats` or eval retrieval provider. |
| `latency_ms` | Event latency in milliseconds. |
| `status` | `ok`, `client_error`, `error`, `completed`, `queued`, `running`, `succeeded`, `failed` or `rate_limited`. |
| `error_code` | HTTP, worker or provider error code when available. |

Event types:

| Event type | Event name | Extra fields |
|---|---|---|
| `api_request` | `api.request` | `route`, `method`, `status_code` |
| `rag_trace` | `rag.query` | `top_k`, `citation_count`, `retrieved_chunk_count`, `fallback_count`, `fallback_reasons`, `retrieval_latency_ms`, `rerank_latency_ms`, `generation_latency_ms`, `query_cache_status`, `rate_limit_status` |
| `eval_metrics` | `eval.run` | `run_id`, `dataset_id`, `dataset_name`, `case_count`, `hit_rate_at_k`, `mrr_at_k`, `recall_at_k`, `average_latency_ms`, `failure_count`, `fallback_count`, `trace_metadata_count` |
| `worker_log` | `worker.task` | `task_id`, `task_type`, `topic`, `eval_run_id`, `idempotency_key`, `attempt`, `max_attempts`, `failure_reason` |

The JSONL exporter must not log raw document text, full prompt bodies, bearer tokens, API keys or production database URLs.

## LogQL Query Examples

API p95 latency:

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

OpenSearch can read the same JSONL schema, but Phase 39 keeps Loki + Grafana as the default local path.

## Phase 40 Dashboard Evidence

Phase 40 adds interview evidence docs and a demo-safe Grafana dashboard skeleton:

- `docs/observability-dashboard-evidence.md`
- `infra/observability/grafana-dashboard-docurag-evidence.json`

The skeleton covers API latency p95, API error rate, worker task failures, RAG retrieval latency, RAG rerank latency, RAG generation latency, fallback count, Hit Rate and MRR. It is importable local evidence only; it is not production alerting, SLO, incident workflow, distributed tracing or APM vendor integration.
