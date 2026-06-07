# OpenAI Compatible Client Boundary

## Goal

新增 OpenAI-compatible provider client boundary，讓 RAG generation / VLM parser / Agent planner 可以透過同一類 provider contract 接不同 inference runtime。

## Scope

- 實作 OpenAI-compatible LLM client adapter，支援 base URL、model、timeout 與 token / latency metadata。
- 保留 Ollama provider fallback，不把 OpenAI-compatible 設為唯一 runtime。
- 補 backend tests，覆蓋 success、timeout、malformed response 與 unavailable fallback。
- 更新 docs / env example。

## Out of Scope

- 不新增 vLLM server 或 Docker runtime；留給 `37-03`。
- 不新增 OpenAI billing integration、API key vault 或 production secret management。
- 不改 RAG prompt、Agent planner 或 VLM parser schema。

## Release Impact

- Target version: `v0.37.0`
- Version bump required: no
- 原因：這是 Phase 37 runtime ticket，版本同步留到 `37-04`。

## Files likely to change

- `backend/app/services/`
- `backend/app/core/`
- `backend/tests/`
- `.env.example`
- `docs/api.md`
- `TODO.md`
- `tasks/phase-37-inference-ops-vllm/37-02-openai-compatible-client-boundary.md`

## Acceptance Criteria

- [ ] OpenAI-compatible provider 可透過 env 明確啟用。
- [ ] Provider 回傳 token / latency metadata，並保留 fallback reason。
- [ ] Ollama fallback 不被移除。
- [ ] Backend tests 覆蓋 provider success 與 error paths。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `rg -n "OpenAI-compatible|base_url|completion tokens|prompt tokens|provider fallback" backend docs TODO.md tasks/phase-37-inference-ops-vllm`
- `git diff --check`
