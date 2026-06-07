# Provider Routing and Fallback

## Goal

實作或補齊 demo-safe inference provider routing，讓 LLM / VLM / embedding / rerank provider unavailable 時能留下清楚 fallback metadata。

## Scope

- 建立 provider selection / health / fallback 的最小 runtime 或 adapter glue。
- 保留既有 Ollama fallback 行為，必要時補充 OpenAI-compatible / vLLM boundary 的 disabled-by-default path。
- 在 trace metadata 中保留 provider selected、provider unavailable、timeout、skip reason 與 fallback target。
- 補充測試與文件，說明 runtime unavailable 不會讓 demo hard fail。

## Out of Scope

- 不啟動 vLLM server，不新增大型模型下載，不新增 paid API key 或 production secret。
- 不把 vLLM 或 OpenAI-compatible endpoint 設為唯一 runtime。
- 不新增 load balancing、多 tenant quota、production circuit breaker service 或 autoscaling。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 42 runtime slice，版本同步留到 `42-05`。

## Files likely to change

- `backend/`
- `docs/`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-42-inference-gateway-capacity-planning/42-02-provider-routing-and-fallback.md`

## Acceptance Criteria

- [ ] Provider routing 可清楚記錄 selected provider 與 fallback reason。
- [ ] Optional provider unavailable 時 demo API 仍可回到既有 fallback。
- [ ] Backend tests 覆蓋 success / unavailable / timeout 或 skip path。

## Validation

- Backend targeted tests。
- Backend full test script。
- `rg -n "provider selected|provider_unavailable|fallback reason|timeout|vLLM|OpenAI-compatible" backend docs README_DEV.md TODO.md tasks/phase-42-inference-gateway-capacity-planning`
- `git diff --check`
