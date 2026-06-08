# Phase 41 Release Sync

## Goal

完成 Phase 41 `v0.41.0` release sync，將 RAG quality regression / DatasetOps 整理成可展示的品質追蹤 milestone。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`。
- 更新 `README.md`、`README_DEV.md`、backend README、frontend README、`TODO.md` 與 `docs/ROADMAP.md`。
- 整理 golden dataset、regression report 與 ablation report 的 validation 結果。
- 明確標示 Phase 41 是品質追蹤與回歸證據，不是 production eval platform。

## Out of Scope

- 不新增 LLM-as-judge、production eval dashboard、資料庫 eval history、排程任務或外部 monitoring。
- 不修改 OCR / parser / Agent / inference core behavior，除非前置 Phase 41 ticket 明確要求。

## Release Impact

- Target version: `v0.41.0`
- Version bump required: yes
- 原因：Phase 41 完成 RAG quality regression / DatasetOps release artifact。

## Files likely to change

- `backend/`
- `frontend/`
- `infra/docker-compose.yml`
- `README.md`
- `README_DEV.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-41-rag-quality-regression-datasetops/41-05-phase-41-release-sync.md`

## Acceptance Criteria

- [x] Backend / frontend / Docker Compose / health test version 同步到 `0.41.0`。
- [x] README / README_DEV 清楚說明 Phase 41 的品質回歸證據。
- [x] Golden dataset、regression report 與 ablation report 都有 validation 紀錄。

## Validation

- Backend tests。
- Frontend build。
- Retrieval regression report smoke。
- Phase 41 keyword `rg` validation。
- `git diff --check`

## Completion Notes

- backend package / app version、frontend package / lock / fallback label、health test、Docker Compose `DOCURAG_VERSION`、`.env.example` 與 demo smoke expected version 已同步到 `0.41.0`。
- README / README_DEV / backend README / frontend README / TODO / ROADMAP 已整理 Phase 41 golden dataset、regression report 與 ablation report validation。
- Phase 41 明確標示為品質追蹤與回歸證據 release，不宣稱 production eval platform、LLM-as-judge、DB eval history、排程任務或外部 monitoring。
