# 23-04 Role Split Demo Release Sync

## Goal

完成 Phase 23 release sync，讓 `v0.23.0` 明確代表 Viewer Chat 與 Admin / Analyst Ingestion 的產品入口拆分，並更新 demo 文件、版本與驗證狀態。

## Scope

- 更新 root README、backend README、frontend README、demo script、architecture、ROADMAP 與 TODO，對齊 Phase 23 完成狀態。
- 同步 `v0.23.0` 版本：
  - backend package / app version
  - frontend package / lock / fallback version
  - health test expected version
  - Docker Compose `DOCURAG_VERSION`
- 更新 demo flow：面試主線先展示 Viewer Chat 查詢既有知識庫，再切到 Admin / Analyst ingestion surface 說明 backend upload + OCR + local chunking。
- 重跑 final validation，確認 baseline Chat、frontend build、demo smoke 與必要文件搜尋都通過。
- 若 demo media 仍引用舊 mixed UI，更新 screenshots 或文件說明。

## Out of Scope

- 不新增登入、RBAC、PostgreSQL、Redis、NATS、worker、async queue、VLM parser、PDF rendering、production indexing、automatic Qdrant indexing、Agent runtime 或 deployment hardening。
- 不改 retrieval algorithm、LLM prompt policy、OCR provider、PaddleOCR lifecycle、sample data 或 eval dataset，除非 validation 發現 Phase 23 UI 文案直接依賴錯誤資料。
- 不建立 release tag，除非使用者或 ticket 後續明確指定。

## Release Impact

- Target version: `v0.23.0`
- Version bump required: yes
- 原因：Phase 23 改變面試 demo 的產品入口與 frontend 使用者流程，完成後應形成新的 release artifact。

## Files likely to change

- `backend/app/core/config.py`
- `backend/pyproject.toml`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/App.vue`
- `frontend/src/styles.css`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/demo-script.md`
- `docs/architecture.md`
- `docs/ROADMAP.md`
- `TODO.md`

## Acceptance Criteria

- [ ] `v0.23.0` 版本與 release docs 已同步。
- [ ] README / demo script 的面試主線是 Viewer Chat first，Admin / Analyst ingestion 為後台管理流程。
- [ ] 文件明確說明 OCR 屬於 backend ingestion layer，前端只展示角色入口與狀態。
- [ ] 文件不宣稱已完成 auth/RBAC、worker、DB、VLM parser、production indexing 或 automatic Qdrant ingestion。
- [ ] Final validation 通過，TODO / ROADMAP 更新 Phase 23 完成狀態。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `cd frontend; npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Browser 檢查 local frontend：Viewer Chat first、Admin / Analyst ingestion surface 分離、無 horizontal overflow。
- `rg -n "v0.23.0|Phase 23|Viewer Chat|Admin / Analyst|Ingestion|知識庫管理|OCR 屬於 backend|role split" README.md backend/README.md frontend/README.md docs/demo-script.md docs/architecture.md docs/ROADMAP.md TODO.md tasks/phase-23-role-split-demo/*.md`
- `git diff --check`
