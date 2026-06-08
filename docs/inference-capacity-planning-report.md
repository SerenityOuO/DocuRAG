# Phase 42 Inference Capacity Planning Report

This report is the Phase 42 capacity planning artifact for the inference gateway track. It connects the Phase 40 hardware benchmark evidence with the Phase 42 provider routing, timeout and fallback decisions.

It is not a production throughput guarantee, not an autoscaling plan and not a claim that vLLM, GPU, NPU or TOPS numbers were measured during this ticket.

## Evidence Inputs

| Input | Role in this report |
|---|---|
| `docs/inference-hardware-benchmark-evidence.md` | Phase 40 hardware evidence baseline for latency, tokens/sec, VRAM, KV cache, TOPS / NPU interpretation and provider skip reason. |
| `scripts/inference-benchmark-smoke.ps1` | Rerunnable benchmark template for OpenAI-compatible / vLLM endpoints. It can produce completed, failed or skipped JSON reports. |
| Phase 42 gateway contract | Defines provider status, fallback target, timeout and capacity planning metadata boundaries. |
| Phase 42 runtime metadata | RAG generation traces now expose provider selected, timeout_ms, max tokens / num_predict, streaming mode, truncated reason and generation latency. |

## Workload Profile

| Workload profile | Request shape | Primary provider path | Context length / prompt tokens | Output tokens | Guardrail | Benchmark status / skip reason |
|---|---|---|---|---|---|---|
| Chat query | User question plus short retrieved answer context. | Ollama or OpenAI-compatible LLM. | Small prompt, usually below 1k prompt tokens in demo data. | `DOCURAG_LLM_NUM_PREDICT=512` max tokens guardrail. | non-streaming, backend timeout, retrieved chunks fallback. | Not re-benchmarked in this ticket; use RAG trace latency and `llm_provider_status`. |
| RAG answer generation | Query plus top retrieved chunks and citation instructions. | Ollama default, OpenAI-compatible optional, vLLM through compatible endpoint. | Depends on top K and chunk size; capacity table uses 4k context length template. | 512 max tokens / num_predict by default. | non-streaming, timeout_ms trace, truncated reason trace. | Existing smoke template can measure compatible endpoint; unavailable endpoint writes skip reason. |
| VLM parser request | Image or document page plus OCR context for invoice parser. | Ollama VLM when enabled, deterministic parser fallback. | Image payload plus OCR context; prompt tokens may be unavailable. | Provider-specific JSON output; no new token estimate fabricated here. | provider timeout, deterministic_invoice fallback. | Not measured here; status should stay `skipped_vlm_runtime_not_benchmarked` unless a real VLM run is recorded. |
| Embedding indexing | Chunk text batch or query text embedding. | FastEmbed / Ollama embedding depending runtime path. | Chunk text input, batch size depends indexing call. | Not applicable. | embedding timeout, vector fallback to keyword retrieval. | Not measured as generation throughput; record indexing latency separately when benchmarked. |
| Rerank request | Query plus candidate chunks. | FastEmbed reranker optional path. | Top candidates, usually top 30 before rerank. | Not applicable. | rerank timeout, original candidates fallback. | Not measured as tokens/sec; benchmark with latency p50 / p95 if needed. |

## Capacity Planning Table

Unknown values remain `pending`, `not_measured` or `skipped`. They must not be converted to zero in README, UI, benchmark JSON or interview notes.

| Provider / workload | concurrency | context length | prompt tokens | completion tokens | p50 latency | p95 latency | tokens/sec / throughput | VRAM peak | KV cache estimate | expected bottleneck | fallback policy | skip reason |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| Ollama small model demo / RAG generation | 1 | 4k template | from trace when available | max 512 guardrail | pending local repeated runs | pending local repeated runs | tokens/sec from provider or trace when available | not_measured_without_gpu_profiler | estimate_if_model_shape_known | model cold start, local GPU memory, long reasoning output | retrieved chunks fallback or deterministic baseline | `ollama_unavailable_if_skipped` |
| vLLM OpenAI-compatible serving / RAG generation | 1-4 template | 4k template | from smoke usage | max 32 smoke, configurable | from `scripts/inference-benchmark-smoke.ps1` repeated runs | from repeated runs | `throughput_tokens_per_second` in smoke report | profiler required | smoke script estimate | KV cache pressure, scheduler queue, VRAM headroom | Ollama or deterministic fallback | `vllm_endpoint_not_running` |
| External OpenAI-compatible endpoint / RAG generation | 1 template | endpoint dependent | provider usage if returned | configured max tokens | provider / gateway measurement required | provider / gateway measurement required | provider usage plus latency | not_applicable_to_local_vram | not_applicable_unless_local_serving | network latency, provider quota, rate limit | retrieved chunks fallback | `provider_unavailable`, `provider_timeout`, `rate_limited` |
| VLM parser request | 1 | image plus OCR context | unavailable unless provider reports usage | JSON output, not fabricated | pending real VLM run | pending real VLM run | not_comparable_to_text_tokens/sec | profiler required | estimate_if_model_shape_known | image preprocessing, vision encoder memory, JSON validity | deterministic_invoice fallback | `skipped_vlm_runtime_not_benchmarked` |
| Embedding indexing | 1 batch template | chunk length dependent | not_applicable | not_applicable | pending indexing benchmark | pending indexing benchmark | chunks/sec or vectors/sec, not tokens/sec | model dependent | not_applicable_for_generation_kv_cache | CPU/GPU embedding throughput, batch size, Qdrant write latency | keyword retrieval fallback | `embedding_runtime_not_benchmarked` |
| Rerank request | 1 | top 30 candidates template | not_applicable | not_applicable | pending rerank benchmark | pending rerank benchmark | candidates/sec, not tokens/sec | model dependent | not_applicable_for_generation_kv_cache | cross-encoder latency, candidate count | original candidates fallback | `rerank_runtime_not_benchmarked` |
| CPU / disabled baseline | 1 | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | no model inference | deterministic answer or retrieved chunks | `no_model_inference` |

## KV Cache Estimate

Use the Phase 40 formula for local decoder-only LLM serving:

```text
kv_cache_estimated_bytes = layer_count * 2 * context_tokens * hidden_size * dtype_bytes * batch_size
```

Example with the benchmark template:

```text
32 * 2 * 4096 * 4096 * 2 * 1 = 2,147,483,648 bytes
```

This is an estimate only. Real VRAM peak also includes model weights, activation memory, allocator overhead, quantization, attention backend, batch scheduling and serving framework behavior.

## TOPS / NPU Interpretation

TOPS is a theoretical hardware operation rate. It is not the same as tokens/sec.

To discuss NPU suitability, record these fields before making a claim:

| Field | Required interpretation |
|---|---|
| TOPS | Hardware theoretical number; useful only with dtype, operator coverage and runtime support. |
| NPU runtime | Driver, SDK, model format and supported operators must be named. |
| measured latency | p50 / p95 latency from real runs, not a vendor spec. |
| throughput | tokens/sec for generation, vectors/sec for embedding, candidates/sec for rerank. |
| unsupported operators | Must be captured as skip reason instead of hidden behind a success row. |

This ticket has no real NPU hardware or TOPS profiler result. Any NPU row must remain `pending_npu_runtime` until measured.

## Provider / Hardware Selection Table

| Option | Best fit | Main risk | Decision note |
|---|---|---|---|
| Small model demo with Ollama | Local interview demo and fallback-friendly RAG answer generation. | Cold start, slower long output, local model availability. | Keep as default demo-safe path when local resources are enough. |
| GPU local serving | Repeatable local benchmark and lower latency than CPU fallback. | VRAM peak, KV cache growth and driver/runtime setup. | Use when `nvidia-smi` or profiler can capture VRAM peak and repeated p50 / p95 latency. |
| CPU / disabled fallback | Deterministic validation and no secret / no model mode. | Not representative of inference throughput. | Use only as control path or demo safety fallback, not capacity evidence. |
| vLLM serving | OpenAI-compatible high-throughput local serving evidence. | Docker/GPU setup, model download size, scheduler tuning. | Use when local endpoint is explicitly started; skipped row is acceptable when endpoint is not running. |
| External OpenAI-compatible endpoint | Enterprise or hosted model integration. | API key, paid usage, network latency, rate limit, data policy. | Keep disabled-by-default unless credentials and policy are explicitly provided. |

## How To Use This Report

1. Pick the workload profile: chat query, RAG answer generation, VLM parser request, embedding indexing or rerank request.
2. Choose the provider row: Ollama demo, vLLM serving, OpenAI-compatible endpoint, CPU / disabled fallback or a measured GPU path.
3. Fill only measured fields from repeated runs. Leave unmeasured p50, p95, VRAM peak, tokens/sec, throughput or KV cache fields as `pending`, `estimate` or `skipped`.
4. Record fallback policy and skip reason before comparing providers.
5. Use the provider / hardware selection table to explain the tradeoff in interviews: local reliability, latency, VRAM pressure, token throughput and operational risk.

## Benchmark Template

Use the existing smoke script for compatible LLM endpoints:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\inference-benchmark-smoke.ps1 -BaseUrl http://127.0.0.1:8000/v1 -Model Qwen/Qwen3-0.6B -OutputPath .tmp/inference-capacity-planning-vllm.json
```

If the endpoint is unavailable, the script should emit a skipped report with provider status, fallback guidance and skip reason. That is valid docs validation for this ticket; it is not a failed capacity result.

## Honesty Boundary

- Do not claim production throughput from a single smoke run.
- Do not fill p50 or p95 latency without repeated runs.
- Do not fill VRAM peak without a profiler such as `nvidia-smi`, Nsight, ROCm SMI or the target NPU profiler.
- Do not compare TOPS to tokens/sec without a measured NPU runtime.
- Do not treat fallback policy as autoscaling, quota management or production rate limiting.
- Do not change default provider, RAG prompt, VLM parser, embedding indexing, rerank behavior or deployment runtime from this report.

## Validation

```powershell
rg -n "capacity planning|KV cache|TOPS|NPU|VRAM|tokens/sec|latency|p50|p95|concurrency|context length|throughput|bottleneck|fallback policy|skip reason|workload profile" docs scripts outputs README_DEV.md TODO.md tasks/phase-42-inference-gateway-capacity-planning
git diff --check
```
