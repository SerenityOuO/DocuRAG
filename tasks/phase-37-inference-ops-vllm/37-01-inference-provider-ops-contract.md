# Inference Provider Ops Contract

## Goal

定義 Phase 37 inference ops / vLLM serving 的 provider boundary、metrics 與 validation contract，讓 Ollama demo path 可擴充到 OpenAI-compatible / vLLM。

## Scope

- 定義 LLM / VLM provider boundary：Ollama、OpenAI-compatible、vLLM。
- 定義 metrics：prompt tokens、completion tokens、latency、throughput、GPU memory estimate、KV cache estimate。
- 定義 provider fallback、timeout、malformed response 與 unavailable handling。
- 更新 docs、TODO、ROADMAP 與 README_DEV。

## Out of Scope

- 不新增 OpenAI-compatible client runtime 或 vLLM server。
- 不新增 multi-GPU serving、autoscaling、K8s deployment 或 production inference gateway。
- 不修改 RAG prompt 主體、Agent planner 或 VLM parser behavior。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 37 contract ticket，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-37-inference-ops-vllm/37-01-inference-provider-ops-contract.md`

## Acceptance Criteria

- [ ] 文件定義 Ollama / OpenAI-compatible / vLLM provider boundary。
- [ ] Metrics contract 包含 token、latency、GPU memory 與 KV cache estimate。
- [ ] Provider fallback 與 timeout policy 清楚。
- [ ] 明確標示本 ticket 不新增 vLLM runtime。

## Validation

- `rg -n "inference|vLLM|OpenAI-compatible|Ollama|KV cache|GPU memory|Phase 37" docs README_DEV.md TODO.md tasks/phase-37-inference-ops-vllm`
- `git diff --check`
