# Inference Ops Phase 37 Release Sync

## Goal

完成 Phase 37 `v0.37.0` release sync，將 OpenAI-compatible provider boundary、vLLM serving guide 與 inference benchmark 形成可展示 release。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.37.0`。
- 更新 README、README_DEV、backend / frontend README、TODO 與 ROADMAP。
- 執行 backend tests、frontend build、baseline demo smoke 與 inference benchmark smoke。
- 記錄 limitation：vLLM 是 serving path / benchmark，不是唯一 runtime 或 production autoscaling。

## Out of Scope

- 不新增 production inference gateway、multi-GPU serving、K8s autoscaling 或 model registry。
- 不新增 OpenAI billing / secret vault integration。
- 不修改 RAG ranking、VLM parser schema 或 Agent planner。

## Release Impact

- Target version: `v0.37.0`
- Version bump required: yes
- 原因：Phase 37 完成 inference ops / vLLM serving demonstration，是 LLMOps-facing release。

## Files likely to change

- `backend/`
- `frontend/`
- `scripts/`
- `infra/docker-compose.yml`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `tasks/phase-37-inference-ops-vllm/37-04-inference-ops-release-sync.md`

## Acceptance Criteria

- [x] `/health` 回傳 `0.37.0`。
- [x] README / README_DEV 說明 OpenAI-compatible / vLLM path 與 fallback。
- [x] Benchmark smoke 記錄 latency / tokens / KV cache 或 skip reason。
- [x] TODO / ROADMAP 記錄 Phase 37 final validation。

## Validation

- [x] `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
  - `251 passed`，1 pytest cache warning。
- [x] `npm.cmd run build`
  - frontend build 通過，package version 顯示 `0.37.0`。
- [x] `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
  - 啟動 local backend 後通過，`/health` version 為 `0.37.0`。
  - 本機 Qdrant unavailable 時 vector indexing fallback 為預期狀態；baseline smoke 仍通過。
- [x] Inference benchmark smoke script：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\inference-benchmark-smoke.ps1`
  - 本機未啟動 vLLM OpenAI-compatible endpoint，script 以 `status=skipped` 寫入 `.tmp/inference-benchmark-smoke.json`，並記錄 provider unavailable skip reason、Ollama / deterministic fallback、KV cache estimate 與 GPU memory estimate。
- [x] `rg -n "v0.37.0|Phase 37|vLLM|OpenAI-compatible|KV cache|GPU memory|latency|tokens" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend scripts tasks/phase-37-inference-ops-vllm`
- [x] `git diff --check`
  - 僅出現 Windows LF/CRLF 換行提示，無 whitespace error。

## Completion Notes

- backend package / app version、health test、Docker Compose `DOCURAG_VERSION` 與 `.env.example` 已同步到 `0.37.0`。
- frontend package / lock version 與 fallback version label 已同步到 `0.37.0`。
- README、README_DEV、backend README、frontend README、TODO 與 ROADMAP 已補上 Phase 37 final status、validation 與 release boundary。
- `scripts/demo-smoke-test.ps1` 的 expected health version 已同步到 `0.37.0`。
- Release boundary 保持明確：vLLM 是 local serving path / benchmark，不是唯一 runtime、production inference gateway、multi-GPU serving、K8s autoscaling、model registry、OpenAI billing / secret vault、RAG ranking 變更、VLM parser schema 變更或 Agent planner。
