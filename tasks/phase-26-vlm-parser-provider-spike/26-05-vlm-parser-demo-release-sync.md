# 26-05 VLM Parser Demo Release Sync

## Goal

完成 Phase 26 final validation 與 `v0.26.0` release sync，讓 demo 可以展示 OCR / image input -> optional VLM parser -> structured fields -> Agent `get_document_fields` consumption 的端到端承接。

## Scope

- 補齊 demo smoke：在 fake / stub VLM provider 或 disabled VLM fallback 情境下，驗證 parser source、fields、fallback reason 與 Agent `get_document_fields` observation。
- 更新 README、backend README、frontend README、docs/demo-script.md、TODO、docs/ROADMAP.md 與必要 API / architecture 文件。
- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `0.26.0` / `v0.26.0`。
- 記錄 Phase 26 demo 說法：目前是 disabled-by-default VLM provider spike，不是 production VLM parser。
- 重跑 backend tests、frontend build、demo smoke、Browser check、ticket `rg` 與 `git diff --check`。

## Out of Scope

- 不新增 production VLM parser、default-on vision runtime、PDF rendering、多頁 parser pipeline、table reconstruction、人工修正 workflow 或 parser dashboard。
- 不新增任意 SQL、PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、Agent permission model、K8s 或 deployment 設定。
- 不修改 Agent planner / tool allowlist；Agent 只消費 `get_document_fields` 保存結果，不直接呼叫 VLM。
- 不新增 release tag，除非使用者明確指定。

## Release Impact

- Target version: `v0.26.0`。
- Version bump required: yes。
- 原因：Phase 26 完成 VLM provider decision、input resolver、disabled-by-default VLM parser adapter、parser source comparison 與 demo validation 後，形成新的 Real VLM Parser Provider Spike release artifact。

## Files likely to change

- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/demo-script.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `backend/app/`
- `backend/tests/`
- `frontend/src/`
- `scripts/demo-smoke-test.ps1`
- `infra/docker-compose.yml`
- `backend/pyproject.toml`
- `frontend/package.json`
- `frontend/package-lock.json`

## Acceptance Criteria

- [ ] Backend / frontend / health / Docker Compose version 已同步到 `0.26.0`。
- [ ] Demo smoke 可驗證 VLM parser disabled fallback 或 fake provider success path。
- [ ] Agent `get_document_fields` observation 可讀到 Phase 26 parser result，不需要改 Agent tool contract。
- [ ] README 與 demo script 說明 Phase 26 是 disabled-by-default VLM provider spike，且不宣稱 production VLM parser。
- [ ] Phase 26 TODO、ROADMAP 與 ticket 狀態同步完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Browser 檢查 local frontend：Viewer Chat first、Admin / Analyst ingestion structured fields、Agent trace consumption、桌面與手機寬度無 horizontal overflow。
- `rg -n "v0.26.0|Phase 26|VLM parser|vlm_invoice|DOCURAG_VLM|parser_source|fallback_reason|get_document_fields" README.md backend/README.md frontend/README.md docs/demo-script.md docs/ROADMAP.md TODO.md backend/app frontend/src tasks/phase-26-vlm-parser-provider-spike`
- `git diff --check`
