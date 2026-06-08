# Phase 40 Inference Hardware Benchmark Evidence

This report is an interview evidence artifact for GPU / NPU, TOPS, KV cache, latency and throughput discussion. It does not claim production capacity, does not start vLLM and does not change the default Ollama / OpenAI-compatible / deterministic fallback behavior.

## Environment

| Field | Evidence value |
|---|---|
| Report purpose | Local inference hardware benchmark template and evidence checklist. |
| Primary script | `scripts/inference-benchmark-smoke.ps1` |
| Default endpoint shape | OpenAI-compatible `/chat/completions` |
| Default local vLLM base URL example | `http://127.0.0.1:8000/v1` |
| Default model example | `Qwen/Qwen3-0.6B` |
| Production guarantee | none; local evidence only |

## Provider Matrix

| Provider path | Command / endpoint | Expected result | Fallback / skip reason |
|---|---|---|---|
| vLLM OpenAI-compatible | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\inference-benchmark-smoke.ps1 -BaseUrl http://127.0.0.1:8000/v1 -Model Qwen/Qwen3-0.6B` | Completed report when a local vLLM endpoint is available. | `status=skipped`, `provider_status=unavailable`, `fallback_target=ollama_or_deterministic` when endpoint is not running. |
| Ollama fallback | Start backend with `DOCURAG_LLM_PROVIDER=ollama`, `DOCURAG_LLM_BASE_URL=http://127.0.0.1:11434`, `DOCURAG_LLM_MODEL=qwen3.5:4b`. | RAG generation can use local Ollama when available. | Use deterministic baseline by setting `DOCURAG_LLM_PROVIDER=` if Ollama is unavailable. |
| OpenAI-compatible adapter | Point backend or smoke script at any compatible `/v1` service. | Records latency, prompt tokens, completion tokens, total tokens and throughput when usage metadata is returned. | Provider timeout, malformed response or unavailable endpoint must produce provider error / skip reason rather than fake success. |
| Deterministic baseline | `DOCURAG_LLM_PROVIDER=` | No hardware inference benchmark; useful as control path. | Not a GPU / NPU serving result. |

## Request Shape

| Field | Default / template |
|---|---|
| prompt | `Reply with exactly: DocuRAG inference benchmark OK.` |
| max output tokens | `32` |
| timeout | `10` seconds |
| batch size | `1` |
| context tokens | `4096` |
| hidden size | `4096` |
| layer count | `32` |
| dtype bytes | `2` |

## Metrics Table

Use the table below for local benchmark evidence. `p50 latency` and `p95 latency` require repeated runs; a single smoke run can only fill one-request latency and should keep percentile fields as pending.

| provider | status | sample count | p50 latency ms | p95 latency ms | time to first token ms | tokens/sec | prompt tokens | completion tokens | VRAM peak MB | KV cache estimated bytes | skip reason |
|---|---|---:|---|---|---|---|---|---|---|---|---|
| vLLM OpenAI-compatible | skipped_template | 0 | pending | pending | pending_streaming_or_server_metric | pending | pending | pending | not_measured_without_gpu_profiler | 2147483648 | vllm_endpoint_not_running |
| vLLM OpenAI-compatible | completed_template | 5+ | fill_from_repeated_runs | fill_from_repeated_runs | fill_from_streaming_or_metrics_endpoint | fill_from_script | fill_from_usage | fill_from_usage | fill_from_nvidia_smi_or_profiler | fill_from_script_estimate | none |
| Ollama fallback | optional_template | 5+ | fill_if_measured | fill_if_measured | fill_if_streaming_measured | fill_if_measured | fill_if_available | fill_if_available | not_measured_without_gpu_profiler | estimate_if_model_shape_known | ollama_unavailable_if_skipped |
| deterministic baseline | control_only | 0 | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | not_applicable | no_model_inference |

## Skip Reason Sections

Use these values when the benchmark cannot produce a measured row. A skipped row is acceptable evidence only when the reason is explicit.

| skip reason | Applies to | Meaning |
|---|---|---|
| `vllm_endpoint_not_running` | vLLM OpenAI-compatible | Local vLLM was not started for this ticket, so the report keeps a rerunnable command instead of fake numbers. |
| `provider_timeout` | vLLM / Ollama / OpenAI-compatible | Endpoint was reachable but did not complete within the configured timeout. |
| `provider_malformed_response` | OpenAI-compatible | Endpoint returned a response that did not include the expected chat completion shape or usage fields. |
| `ollama_unavailable_if_skipped` | Ollama fallback | Local Ollama service or model was not available during an optional fallback check. |
| `no_model_inference` | deterministic baseline | Control path does not run GPU / NPU inference and should not be compared as a hardware benchmark. |

## KV Cache Estimate

The smoke script uses this estimate:

```text
kv_cache_estimated_bytes = layer_count * 2 * context_tokens * hidden_size * dtype_bytes * batch_size
```

With the default template values, this is:

```text
32 * 2 * 4096 * 4096 * 2 * 1 = 2,147,483,648 bytes
```

That is an estimate only. Real VRAM peak depends on model weights, backend implementation, allocator behavior, quantization, batching, speculative decoding, attention backend and active scheduler state.

## TOPS / NPU Interpretation

TOPS is a hardware throughput specification, not a direct answer to tokens/sec. A useful interview explanation should separate:

- hardware theoretical TOPS,
- model dtype and quantization,
- memory bandwidth and KV cache pressure,
- operator support on the NPU runtime,
- end-to-end latency including tokenization, scheduling and network overhead.

This ticket does not run an NPU profiler and does not claim measured TOPS. If a future NPU runtime is tested, record profiler name, driver version, model format, quantization, p50 / p95 latency, time to first token, throughput and skip reason for unsupported operators.

## vLLM Command Template

Local vLLM serving can be started outside this ticket using the existing local setup guide:

```powershell
docker run --gpus all --ipc=host -p 8000:8000 vllm/vllm-openai:latest --model Qwen/Qwen3-0.6B
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\inference-benchmark-smoke.ps1 -BaseUrl http://127.0.0.1:8000/v1 -Model Qwen/Qwen3-0.6B -OutputPath outputs/inference-benchmark-vllm.json
```

Metrics endpoint note: vLLM deployments may expose Prometheus metrics depending on server flags and version. If available, use the metrics endpoint to cross-check request latency, scheduler state and token throughput; if unavailable, keep `metrics_endpoint=not_available` in the report.

## Honesty Boundary

- This is benchmark evidence, not production capacity planning.
- Do not compare NPU TOPS claims to tokens/sec without a real runtime measurement.
- Do not fill VRAM peak without a profiler such as `nvidia-smi`, Nsight, ROCm SMI or the target NPU profiler.
- Do not treat `status=skipped` as a failure when the ticket only asks for skip-safe evidence.
- Do not change RAG prompt, Agent planner, VLM parser, OCR pipeline, default provider or deployment runtime from this report.

## Validation

```powershell
rg -n "inference benchmark|KV cache|TOPS|NPU|VRAM|tokens/sec|latency|p50|p95|time to first token|throughput|vLLM|Ollama|OpenAI-compatible|skip reason|metrics endpoint" docs scripts README_DEV.md TODO.md tasks/phase-40-interview-evidence-hardening
git diff --check
```
