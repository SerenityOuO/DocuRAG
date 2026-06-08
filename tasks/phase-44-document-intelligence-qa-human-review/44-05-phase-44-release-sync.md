# Phase 44 Release Sync

## Goal

完成 Phase 44 `v0.44.0` release sync，將 Document Intelligence QA / human review loop 整理成可展示的文件理解可信度 milestone。

## Scope

- 同步 backend version、frontend package version、frontend fallback version、health test、Docker Compose `DOCURAG_VERSION`。
- 更新 `README.md`、`README_DEV.md`、backend README、frontend README、`TODO.md` 與 `docs/ROADMAP.md`。
- 整理 field confidence / evidence view、human correction / golden labels 與 parser field accuracy eval 的 validation。
- 明確標示 Phase 44 是 demo-safe QA loop，不是 production annotation platform。

## Out of Scope

- 不新增 production annotation workflow、layout analysis、table reconstruction、model training 或 production OCR accuracy tuning。
- 不修改 RAG / Agent / inference core behavior，除非前置 Phase 44 ticket 明確要求。

## Release Impact

- Target version: `v0.44.0`
- Version bump required: yes
- 原因：Phase 44 完成 Document Intelligence QA / human review loop release artifact。

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
- `tasks/phase-44-document-intelligence-qa-human-review/44-05-phase-44-release-sync.md`

## Acceptance Criteria

- [x] Backend / frontend / Docker Compose / health test version 同步到 `0.44.0`。
- [x] README / README_DEV 清楚說明 Phase 44 文件理解 QA 能力與邊界。
- [x] Field confidence、human correction、golden labels 與 parser eval 都有 validation 紀錄。

## Validation

- Backend tests。
- Frontend build。
- Parser field accuracy smoke。
- Browser validation if UI changed。
- Phase 44 keyword `rg` validation。
- `git diff --check`

## Completion Notes

- Backend package / app version、frontend package / lock / fallback label、health test、Docker Compose `DOCURAG_VERSION` 與 `.env.example` 已同步到 `0.44.0`。
- README、README_DEV、backend README、frontend README、TODO 與 ROADMAP 已整理 Phase 44 field confidence / evidence view、human correction / golden labels 與 parser field accuracy eval 的展示能力、validation 與 boundary。
- Validation 已通過：backend full test `270 passed, 1 warning`（pytest cache permission warning）、frontend build、parser field accuracy smoke（field accuracy `0.6`、sample count `5`、missing / wrong / evidence mismatch 各 `1`）、Phase 44 keyword `rg` 與 `git diff --check`。Browser validation 未重跑，因本 release sync 只同步 fallback version label 與文件，未新增或重排 UI surface。
- 本 release 仍是 demo-safe Document Intelligence QA / human review loop，不是 production annotation platform、layout analysis、table reconstruction、model training 或 production OCR accuracy tuning。
