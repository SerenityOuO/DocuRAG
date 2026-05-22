# 19-04 Hybrid Rerank Demo Release Sync

## Goal

完成 Phase 19 `hybrid_rerank` implementation release，重跑必要 validation，更新版本與文件，形成 `v0.19.0` release artifact。

## Scope

- 重跑 backend tests、frontend build、baseline demo smoke 與 baseline retrieval eval smoke。
- 在本機 optional runtime 可用時，重跑 optional vector、`vector_rerank`、`hybrid` 與 `hybrid_rerank` eval smoke；不可用時需明確記錄 preflight 條件與 fallback。
- 更新 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP。
- 更新 Phase 19 checklist 與 release verification status。
- 確認 `hybrid_rerank` 仍是 explicit optional eval strategy，不接 default `/rag/query` 或 production dashboard。

## Out of Scope

- 不新增 frontend production eval dashboard、strategy comparison page、live eval runner、backend API endpoint 或 default chat hybrid rerank。
- 不新增 BM25 dependency、query rewriting、LLM-as-judge、answer faithfulness scoring、citation quality scoring 或 release tag。
- 不新增 Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、Agent runtime、VLM parser、PDF rendering、production OCR pipeline、K8s 或 deployment 設定。

## Release Impact

- Target version: `v0.19.0`。
- Version bump required: yes。
- 原因：`19-04` 完成後，Phase 19 `hybrid_rerank` implementation 已具備 eval provider、smoke flag、trace/report visibility、validation 與 release 文件同步，形成 `v0.19.0` release artifact。

## Files likely to change

- `backend/app/core/config.py`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/App.vue`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 同步到 `0.19.0`。
- [ ] README、backend README、frontend README、TODO 與 ROADMAP 都記錄 `v0.19.0` `hybrid_rerank` release status。
- [ ] Baseline demo smoke 與 baseline retrieval eval smoke 通過。
- [ ] Optional `hybrid_rerank` smoke 狀態被明確記錄，不因 optional runtime 不可用而破壞 baseline release。
- [ ] Phase 19 沒有新增 out-of-scope dashboard、auth、DB、worker 或 deployment 功能。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`（於 `frontend/`）
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVector`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVectorRerank`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybrid`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybridRerank`
- `rg -n "v0.19.0|Phase 19|hybrid_rerank|RunHybridRerank" README.md backend/README.md frontend/README.md TODO.md docs/ROADMAP.md scripts backend/app backend/tests`
- `git diff --check`
