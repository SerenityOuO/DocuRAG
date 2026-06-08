# Capacity Planning Report

## Goal

建立 inference capacity planning report，展示 latency、tokens/sec、VRAM、KV cache、TOPS / NPU 評估方式與 provider fallback / skip reason。

## Scope

- 新增或更新 benchmark report / template，記錄 prompt size、output tokens、latency、tokens/sec、VRAM usage、KV cache estimate。
- 補充 vLLM / Ollama / OpenAI-compatible provider 的 benchmark success / skip reason。
- 說明 GPU / NPU / TOPS 的評估方式，不假裝有未實測硬體結果。
- 將結果連回 Phase 40 inference hardware evidence 與 Phase 42 gateway decision。
- Report 必須包含 workload profile：chat query、RAG answer generation、VLM parser request、embedding indexing 與 rerank request 的 request shape。
- Capacity table 至少列出 concurrency、context length、prompt tokens、completion tokens、p50 / p95 latency、tokens/sec、VRAM peak、KV cache estimate、expected bottleneck 與 fallback policy。
- 補充「模型 / 硬體選型」決策表：小模型 demo、GPU local serving、CPU fallback、vLLM serving、OpenAI-compatible endpoint 各自適用場景與風險。

## Out of Scope

- 不要求真實 NPU 硬體或 TOPS profiler。
- 不下載大型模型、不啟動長時間 benchmark、不承諾 production throughput。
- 不新增 production metrics service 或 autoscaling controller。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 42 capacity planning artifact ticket，版本同步留到 `42-05`。

## Files likely to change

- `docs/`
- `scripts/`
- `outputs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-42-inference-gateway-capacity-planning/42-04-capacity-planning-report.md`

## Acceptance Criteria

- [x] Report 包含 latency、tokens/sec、VRAM、KV cache estimate 與 provider skip reason。
- [x] TOPS / NPU 評估方式清楚標示為估算或待測，不假裝已實測。
- [x] 文件說明如何用 report 做模型 / 硬體選型。
- [x] Workload profile 覆蓋 RAG generation、VLM parser、embedding indexing 與 rerank request。
- [x] Capacity table 包含 concurrency、context length、p50 / p95 latency、tokens/sec、VRAM peak、KV cache estimate、bottleneck 與 fallback policy。
- [x] Provider 選型表清楚比較 Ollama、vLLM、OpenAI-compatible endpoint 與 CPU / disabled fallback。

## Validation

- Benchmark template smoke 或 docs validation。
- `rg -n "capacity planning|KV cache|TOPS|NPU|VRAM|tokens/sec|latency|p50|p95|concurrency|context length|throughput|bottleneck|fallback policy|skip reason|workload profile" docs scripts outputs README_DEV.md TODO.md tasks/phase-42-inference-gateway-capacity-planning`
- `git diff --check`

## Completion Notes

- Added `docs/inference-capacity-planning-report.md` as the Phase 42 capacity planning artifact.
- Report links Phase 40 hardware benchmark evidence, `scripts/inference-benchmark-smoke.ps1` and Phase 42 gateway decisions.
- Workload profile covers chat query, RAG answer generation, VLM parser request, embedding indexing and rerank request.
- Capacity table keeps unmeasured p50 / p95 latency, tokens/sec / throughput, VRAM peak and hardware profiler fields as `pending`, `estimate`, `not_measured` or `skipped`.
- Version bump required: no. Phase 42 version sync remains scoped to `42-05`.
