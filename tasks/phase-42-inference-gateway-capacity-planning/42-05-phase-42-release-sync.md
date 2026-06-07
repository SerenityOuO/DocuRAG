# Phase 42 Release Sync

## Goal

完成 Phase 42 `v0.42.0` release sync，將 inference gateway 與 capacity planning 整理成可展示的推論維運 milestone。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`。
- 更新 `README.md`、`README_DEV.md`、backend README、frontend README、`TODO.md` 與 `docs/ROADMAP.md`。
- 整理 provider routing、timeout guardrails 與 capacity planning report 的 validation。
- 明確標示 Phase 42 是 demo-safe inference ops，不是 production autoscaling 或多 GPU serving。

## Out of Scope

- 不新增 production autoscaling、多 GPU serving、paid API key、production secret 或 SLA。
- 不修改 OCR / parser / RAG / Agent behavior，除非前置 Phase 42 ticket 明確要求。

## Release Impact

- Target version: `v0.42.0`
- Version bump required: yes
- 原因：Phase 42 完成 inference gateway / capacity planning release artifact。

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
- `tasks/phase-42-inference-gateway-capacity-planning/42-05-phase-42-release-sync.md`

## Acceptance Criteria

- [ ] Backend / frontend / Docker Compose / health test version 同步到 `0.42.0`。
- [ ] README / README_DEV 清楚說明 Phase 42 的 inference ops 證據與邊界。
- [ ] Provider routing、timeout guardrails 與 capacity planning report 都有 validation 紀錄。

## Validation

- Backend tests。
- Frontend build。
- Inference gateway smoke 或 skip-safe validation。
- Phase 42 keyword `rg` validation。
- `git diff --check`
