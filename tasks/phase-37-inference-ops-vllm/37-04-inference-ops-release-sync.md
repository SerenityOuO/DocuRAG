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

- [ ] `/health` 回傳 `0.37.0`。
- [ ] README / README_DEV 說明 OpenAI-compatible / vLLM path 與 fallback。
- [ ] Benchmark smoke 記錄 latency / tokens / KV cache 或 skip reason。
- [ ] TODO / ROADMAP 記錄 Phase 37 final validation。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Inference benchmark smoke script。
- `rg -n "v0.37.0|Phase 37|vLLM|OpenAI-compatible|KV cache|GPU memory|latency|tokens" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend scripts tasks/phase-37-inference-ops-vllm`
- `git diff --check`
