# Inference Hardware Benchmark Evidence

## Goal

建立推論硬體 benchmark report，補強 JD 中 GPU / NPU、TOPS、KV cache、latency、throughput 與 vLLM / Ollama / OpenAI-compatible serving 的可展示證據。

## Scope

- 新增或更新 inference benchmark docs，記錄測試環境、模型、provider、prompt size、output tokens、latency、tokens/sec、VRAM usage 與 KV cache estimate。
- 補充 TOPS / NPU 評估方式：可用文字說明與估算表，不要求實際 NPU runtime。
- 若有 vLLM / Ollama smoke，記錄 success / skip reason，不讓 runtime unavailable 造成文件不可信。
- 補 benchmark script 或 report template，讓後續可以重跑並更新數據。

## Out of Scope

- 不新增 production inference gateway、multi-GPU serving、autoscaling 或 model registry。
- 不要求實際 NPU 硬體或 TOPS profiler。
- 不更換 default LLM / VLM / embedding / rerank provider。
- 不修改 RAG prompt、Agent planner、VLM parser 或 OCR pipeline。

## Release Impact

- Target version: `v0.40.0`
- Version bump required: no
- 原因：這是 Phase 40 evidence artifact ticket，版本同步留到 `40-05`。

## Files likely to change

- `docs/`
- `scripts/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-40-interview-evidence-hardening/40-03-inference-hardware-benchmark-evidence.md`

## Acceptance Criteria

- [ ] 有一份 inference hardware benchmark report 或 template。
- [ ] Report 包含 latency、tokens/sec、VRAM、KV cache estimate 與 provider fallback / skip reason。
- [ ] TOPS / NPU 評估方式有清楚說明，不假裝已實測沒有的硬體。
- [ ] Benchmark script 或手動 validation 步驟可被後續重跑。
- [ ] 文件明確標示 benchmark 是 local evidence，不是 production capacity guarantee。

## Validation

- `rg -n "inference benchmark|KV cache|TOPS|NPU|VRAM|tokens/sec|latency|throughput|vLLM|Ollama|OpenAI-compatible" docs scripts README_DEV.md TODO.md tasks/phase-40-interview-evidence-hardening`
- `git diff --check`
