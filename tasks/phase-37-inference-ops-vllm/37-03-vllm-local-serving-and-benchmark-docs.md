# vLLM Local Serving and Benchmark Docs

## Goal

新增 vLLM local serving path 與 inference benchmark docs / smoke，展示推論維運能力與 latency / token / KV cache 觀測。

## Scope

- 新增 vLLM local / Docker serving guide，使用 OpenAI-compatible endpoint。
- 新增 benchmark script 或 smoke，記錄 latency、tokens、throughput 與 KV cache / GPU memory estimate。
- 文件說明 hardware constraints 與 fallback to Ollama / deterministic path。
- 補 validation 紀錄格式。

## Out of Scope

- 不把 vLLM 設為唯一 default runtime。
- 不新增 multi-GPU serving、production autoscaling、K8s inference deployment 或 model registry。
- 不修改 RAG / VLM / Agent prompts 或 ranking behavior。

## Release Impact

- Target version: `v0.37.0`
- Version bump required: no
- 原因：這是 Phase 37 ops / docs / smoke ticket，版本同步留到 `37-04`。

## Files likely to change

- `scripts/`
- `docs/`
- `README_DEV.md`
- `.env.example`
- `infra/`
- `TODO.md`
- `tasks/phase-37-inference-ops-vllm/37-03-vllm-local-serving-and-benchmark-docs.md`

## Acceptance Criteria

- [ ] Docs 說明如何啟動 vLLM OpenAI-compatible endpoint。
- [ ] Benchmark / smoke 可記錄 token、latency、throughput 與 KV cache / GPU estimate。
- [ ] vLLM unavailable 時有明確 skip / fallback 說明。
- [ ] 文件不宣稱 production inference serving 完成。

## Validation

- Inference benchmark smoke script。
- `rg -n "vLLM|OpenAI-compatible|KV cache|GPU memory|throughput|latency" scripts docs README_DEV.md TODO.md tasks/phase-37-inference-ops-vllm`
- `git diff --check`
