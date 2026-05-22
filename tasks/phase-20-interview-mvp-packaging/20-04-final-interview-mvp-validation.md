# 20-04 Final Interview MVP Validation

## Goal

完成 Phase 20 面試 MVP 收斂，重跑必要 validation，更新 release/version 文件，並形成 `v0.20.0` interview MVP packaging release artifact。

## Scope

- 重跑 backend tests、frontend build、baseline demo smoke 與 baseline retrieval eval smoke。
- 在本機 optional runtime 可用時，重跑 optional vector、`vector_rerank` 與 `hybrid` eval smoke；不可用時需明確記錄 preflight 條件與 fallback。
- 更新 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`、README、backend README、frontend README、TODO 與 ROADMAP。
- 確認 Phase 20 沒有偏離 interview MVP packaging scope，沒有偷渡 Auth / DB / Redis / NATS / worker / deployment。
- 更新 Phase 20 checklist 與 release verification status。

## Out of Scope

- 不實作 `hybrid_rerank` runtime、BM25 dependency、query rewriting、LLM-as-judge、answer faithfulness scoring、citation quality scoring 或 production eval dashboard。
- 不新增 backend API、frontend route、DB schema、Redis、NATS、worker、Auth、RBAC、Agent runtime、K8s 或 deployment 設定。
- 不新增 release tag，除非 ticket 或使用者另行明確指定。

## Release Impact

- Target version: `v0.20.0`。
- Version bump required: yes。
- 原因：`20-04` 完成後，Phase 20 interview MVP packaging 已具備更新後 demo docs、sample/eval coverage、demo media、validation 與 release 文件同步，形成 `v0.20.0` release artifact。

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

- [ ] Backend version、frontend package version、frontend fallback version、health test 與 Docker Compose `DOCURAG_VERSION` 同步到 `0.20.0`。
- [ ] README、backend README、frontend README、TODO 與 ROADMAP 都記錄 `v0.20.0` interview MVP packaging release status。
- [ ] Baseline demo smoke 與 baseline retrieval eval smoke 通過。
- [ ] Optional strategy smoke 的狀態被明確記錄，不因 optional runtime 不可用而破壞 baseline release。
- [ ] Phase 20 沒有新增 out-of-scope runtime、infra、auth、DB 或 deployment 功能。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`（於 `frontend/`）
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVector`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunVectorRerank`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybrid`
- `rg -n "v0.20.0|Phase 20|interview MVP|面試 MVP" README.md backend/README.md frontend/README.md TODO.md docs/ROADMAP.md`
- `git diff --check`
