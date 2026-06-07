# Inference Gateway Contract

## Goal

定義 Phase 42 inference gateway / capacity planning 的邊界，讓 Ollama、vLLM 與 OpenAI-compatible endpoint 有一致的 routing、fallback 與觀測欄位。

## Scope

- 定義 provider domain：Ollama、vLLM、OpenAI-compatible endpoint 與 disabled fallback。
- 定義 request / response metadata：model、provider、prompt tokens、completion tokens、latency、tokens/sec、timeout、fallback reason。
- 定義 routing policy、retry policy、provider health 與 circuit breaker 的文件邊界。
- 定義哪些能力屬於 capacity planning report，而不是 runtime 強制保證。

## Out of Scope

- 不新增 provider runtime、streaming API、OpenAI SDK、vLLM server 或 Docker service。
- 不修改現有 Ollama LLM / VLM / embedding 行為。
- 不宣稱 production autoscaling、多 GPU serving 或 SLA。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 42 contract ticket，只定義 gateway 邊界，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-42-inference-gateway-capacity-planning/42-01-inference-gateway-contract.md`

## Acceptance Criteria

- [ ] 文件定義 Ollama / vLLM / OpenAI-compatible provider gateway 邊界。
- [ ] 文件列出 routing、fallback、timeout、token usage 與 latency metadata。
- [ ] 文件明確說明 Phase 42 不承諾 production autoscaling。

## Validation

- `rg -n "Phase 42|inference gateway|Ollama|vLLM|OpenAI-compatible|routing|fallback|tokens/sec|circuit breaker" docs README_DEV.md TODO.md tasks/phase-42-inference-gateway-capacity-planning`
- `git diff --check`
