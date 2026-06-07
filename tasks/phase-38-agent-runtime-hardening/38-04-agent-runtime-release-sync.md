# Agent Runtime Phase 38 Release Sync

## Goal

完成 Phase 38 `v0.38.0` release sync，將 LLM planner boundary、tool permission guards 與 Agent trace hardening 形成可展示 release。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `v0.38.0`。
- 更新 README、README_DEV、backend / frontend README、TODO 與 ROADMAP。
- 執行 backend tests、frontend build、Agent smoke 與 Browser validation。
- 記錄 limitation：仍不允許任意 SQL、shell、filesystem 或 destructive tools。

## Out of Scope

- 不新增 arbitrary autonomous agent、destructive tool execution、任意 SQL、shell 或 filesystem command。
- 不新增 enterprise approval workflow、external browser control 或 production audit dashboard。
- 不修改 OCR / parser / RAG ranking 或 inference provider default。

## Release Impact

- Target version: `v0.38.0`
- Version bump required: yes
- 原因：Phase 38 完成 Agent runtime hardening，是 user-facing / architecture-facing release。

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
- `tasks/phase-38-agent-runtime-hardening/38-04-agent-runtime-release-sync.md`

## Acceptance Criteria

- [ ] `/health` 回傳 `0.38.0`。
- [ ] Agent smoke 驗證 planner fallback、tool permission guard 與 trace。
- [ ] README / README_DEV 說明 Agent runtime hardening 與 forbidden tool boundary。
- [ ] TODO / ROADMAP 記錄 Phase 38 validation。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- Agent runtime smoke script。
- Browser 檢查 Agent trace desktop / mobile。
- `rg -n "v0.38.0|Phase 38|Agent|LLM planner|tool permission|destructive|fallback" README.md README_DEV.md backend/README.md frontend/README.md docs/ROADMAP.md TODO.md backend frontend scripts tasks/phase-38-agent-runtime-hardening`
- `git diff --check`
