# 24-05 Parser Demo Release Sync

## Goal

完成 Phase 24 final validation 與 `v0.24.0` release sync，讓 demo 從 upload -> OCR -> local chunks -> RAG 擴充為 upload -> OCR -> structured fields -> RAG 的可展示流程。

## Scope

- 補齊 smoke script 或 demo validation，驗證 upload、OCR、parse、fields lookup 與 baseline RAG query。
- 同步 backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 到 `0.24.0`。
- 更新 `README.md`、`backend/README.md`、`frontend/README.md`、`TODO.md`、`docs/ROADMAP.md` 與 `docs/demo-script.md`。
- 記錄 Phase 24 demo 說法：目前是 deterministic parser MVP / VLM-compatible contract，不是 production VLM parser。
- 重跑 backend tests、frontend build、baseline demo smoke 與必要 `rg` / `git diff --check`。

## Out of Scope

- 不新增真正 VLM、Ollama vision call、OpenAI-compatible VLM、LLM parser 或新外部依賴。
- 不新增 PostgreSQL schema、migration、Redis、NATS、worker、async queue、Auth、RBAC、Agent runtime、K8s 或 deployment 設定。
- 不實作人工修正欄位、欄位版本紀錄、audit log、表格完整重建、PDF rendering、多頁 production OCR pipeline 或 production parser dashboard。
- 不把 structured fields 接成 SQL query tool、Agent tool 或 default vector metadata filtering。
- 不建立 release tag。

## Release Impact

- Target version: `v0.24.0`。
- Version bump required: yes。
- 原因：Phase 24 完成 parser contract、deterministic invoice parser、parse / fields API、frontend structured fields surface 與 demo validation 後，形成新的 VLM / Parser Minimal MVP release artifact。

## Files likely to change

- `backend/pyproject.toml`
- `backend/app/core/config.py`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/api/client.ts`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `docs/demo-script.md`
- `scripts/demo-smoke-test.ps1`

## Acceptance Criteria

- [ ] Backend / frontend / Docker Compose / health test versions 同步到 `0.24.0`。
- [ ] Demo smoke 可驗證 OCR 後 parse 與 fields lookup。
- [ ] README 與 demo script 說明 structured fields demo，且不宣稱 production VLM parser。
- [ ] Phase 24 TODO、ROADMAP 與 ticket 狀態同步完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- Browser 檢查 local frontend：Viewer Chat first、Admin / Analyst ingestion structured fields surface、桌面與手機寬度無 horizontal overflow。
- `rg -n "v0.24.0|Phase 24|Parser|structured fields|欄位解析|VLM-compatible|DocumentFields|ExtractedField" README.md backend/README.md frontend/README.md docs/demo-script.md docs/ROADMAP.md TODO.md backend/app frontend/src tasks/phase-24-vlm-parser-mvp`
- `git diff --check`
