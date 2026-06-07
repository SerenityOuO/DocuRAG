# Capacity Planning Report

## Goal

建立 inference capacity planning report，展示 latency、tokens/sec、VRAM、KV cache、TOPS / NPU 評估方式與 provider fallback / skip reason。

## Scope

- 新增或更新 benchmark report / template，記錄 prompt size、output tokens、latency、tokens/sec、VRAM usage、KV cache estimate。
- 補充 vLLM / Ollama / OpenAI-compatible provider 的 benchmark success / skip reason。
- 說明 GPU / NPU / TOPS 的評估方式，不假裝有未實測硬體結果。
- 將結果連回 Phase 40 inference hardware evidence 與 Phase 42 gateway decision。

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

- [ ] Report 包含 latency、tokens/sec、VRAM、KV cache estimate 與 provider skip reason。
- [ ] TOPS / NPU 評估方式清楚標示為估算或待測，不假裝已實測。
- [ ] 文件說明如何用 report 做模型 / 硬體選型。

## Validation

- Benchmark template smoke 或 docs validation。
- `rg -n "capacity planning|KV cache|TOPS|NPU|VRAM|tokens/sec|latency|throughput|skip reason" docs scripts outputs README_DEV.md TODO.md tasks/phase-42-inference-gateway-capacity-planning`
- `git diff --check`
