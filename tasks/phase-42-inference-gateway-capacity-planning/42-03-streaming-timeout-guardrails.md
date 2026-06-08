# Streaming Timeout Guardrails

## Goal

補強 inference request 的 timeout、streaming boundary 與 demo latency guardrails，讓長輸出或 provider slow path 不拖垮展示流程。

## Scope

- 定義或實作 server-side timeout、max tokens、streaming disabled / enabled boundary。
- 補充 trace metadata：timeout_ms、num_predict、streaming mode、truncated reason、generation latency。
- 文件說明何時使用 streaming，何時保留 non-streaming demo path。
- 保留目前 Ollama generation guardrails，不擴張到完整 frontend token streaming，除非本 ticket 明確列入。

## Out of Scope

- 不新增完整 SSE / WebSocket frontend streaming UI，除非另開 UI ticket。
- 不新增 queue-based inference scheduler、多使用者 quota 或 production rate limiter。
- 不更換預設模型或新增外部 inference dependency。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 42 guardrail ticket，版本同步留到 `42-05`。

## Files likely to change

- `backend/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-42-inference-gateway-capacity-planning/42-03-streaming-timeout-guardrails.md`

## Acceptance Criteria

- [x] Timeout / token limit / streaming mode 在文件或 trace metadata 中清楚可見。
- [x] Slow provider path 有 fallback 或 clear failure reason。
- [x] Validation 覆蓋 timeout / guardrail behavior。

## Validation

- Backend targeted tests。
- Backend full test script。
- `rg -n "timeout|streaming|num_predict|max tokens|generation latency|truncated|guardrail" backend docs README_DEV.md TODO.md tasks/phase-42-inference-gateway-capacity-planning`
- `git diff --check`

## Completion Notes

- RAG LLM generation trace now records `llm_timeout_ms`, `llm_num_predict`, `llm_max_tokens`, `llm_streaming_mode`, `llm_truncated_reason` and `llm_generation_latency_ms`.
- Ollama and OpenAI-compatible generation remain non-streaming (`stream=false`) for the demo API path; no frontend SSE / WebSocket streaming UI was added.
- Provider timeout is classified as `llm_provider_status=timeout`, keeps `llm_fallback_target=retrieved_chunks` and preserves the bounded error in `llm_error`.
- Version bump required: no. Phase 42 version sync remains scoped to `42-05`.
