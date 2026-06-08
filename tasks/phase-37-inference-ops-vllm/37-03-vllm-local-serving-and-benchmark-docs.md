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

- [x] Docs 說明如何啟動 vLLM OpenAI-compatible endpoint。
- [x] Benchmark / smoke 可記錄 token、latency、throughput 與 KV cache / GPU estimate。
- [x] vLLM unavailable 時有明確 skip / fallback 說明。
- [x] 文件不宣稱 production inference serving 完成。

## Validation

- [x] Inference benchmark smoke script：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\inference-benchmark-smoke.ps1`
  - 本機未啟動 vLLM OpenAI-compatible endpoint，script 以 `status=skipped` 寫入 `.tmp/inference-benchmark-smoke.json`，並記錄 `provider_status=unavailable`、skip reason、Ollama / deterministic fallback 與 KV cache / GPU memory estimate。
- [x] `rg -n "vLLM|OpenAI-compatible|KV cache|GPU memory|throughput|latency" scripts docs README_DEV.md TODO.md tasks/phase-37-inference-ops-vllm`
- [x] `git diff --check`
  - 僅出現 Windows LF/CRLF 換行提示，無 whitespace error。

## Completion Notes

- 新增 `scripts/inference-benchmark-smoke.ps1`，可對 OpenAI-compatible `/v1/chat/completions` endpoint 記錄 latency、prompt tokens、completion tokens、total tokens、throughput、finish reason、provider request id、KV cache estimate 與 GPU memory estimate。
- `docs/LOCAL_DEV_SETUP.md` 補上 vLLM Docker / OpenAI-compatible local serving guide、官方 vLLM docs 連結、hardware constraints 與 fallback 說明。
- `.env.example` 與 `infra/docker-compose.yml` 補上 local OpenAI-compatible / vLLM env pass-through；未新增 vLLM service，也未改變 default provider。
- `README_DEV.md`、`TODO.md`、`docs/ROADMAP.md` 與 `docs/architecture.md` 已同步 37-03 狀態與邊界。
