# Phase 43 Release Sync

## Goal

完成 Phase 43 `v0.43.0` release sync，將 AgentOps governance / secure tool runtime 整理成可展示的 Agent 安全治理 milestone。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`。
- 更新 `README.md`、`README_DEV.md`、backend README、frontend README、`TODO.md` 與 `docs/ROADMAP.md`。
- 整理 tool permission、approval state 與 Agent replay / eval 的 validation。
- 明確標示 Phase 43 不代表 production autonomous Agent 或外部 side-effect tool runtime。

## Out of Scope

- 不新增任意 SQL、shell、filesystem command、destructive tools、production IAM 或 external approval workflow。
- 不修改 OCR / parser / RAG / inference core behavior，除非前置 Phase 43 ticket 明確要求。

## Release Impact

- Target version: `v0.43.0`
- Version bump required: yes
- 原因：Phase 43 完成 AgentOps governance / secure tool runtime release artifact。

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
- `tasks/phase-43-agentops-governance-secure-runtime/43-05-phase-43-release-sync.md`

## Acceptance Criteria

- [ ] Backend / frontend / Docker Compose / health test version 同步到 `0.43.0`。
- [ ] README / README_DEV 清楚說明 Phase 43 Agent governance 能力與邊界。
- [ ] Tool permission、approval state 與 Agent replay / eval 都有 validation 紀錄。

## Validation

- Backend tests。
- Frontend build。
- Agent governance / replay smoke。
- Phase 43 keyword `rg` validation。
- `git diff --check`
