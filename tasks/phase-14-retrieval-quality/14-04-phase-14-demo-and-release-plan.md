# 14-04 Phase 14 Demo and Release Plan

## Goal

規劃 Phase 14 / `v0.14.0` 的 demo、validation 與 release 文件同步方式，確保後續若實作 rerank / hybrid search 時能用 Phase 13 eval baseline 做可重跑比較。此 ticket 只做計畫，不執行 release sync。

## Scope

- 規劃 future rerank / hybrid demo smoke 的 preflight 順序與 expected output。
- 定義 future validation checklist，包含 backend tests、frontend build、baseline eval、optional strategy eval 與 `git diff --check`。
- 規劃 release sync checklist，列出若未來完成 v0.14.0 runtime release 時需要同步的檔案。
- 明確記錄 Phase 14 planning 完成後，真正 runtime implementation 需另開後續 ticket。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 14 release planning 狀態。

## Out of Scope

- 不修改 backend version、frontend package version、frontend fallback version、health test 或 Docker Compose `DOCURAG_VERSION`。
- 不新增或修改 demo smoke script。
- 不新增 rerank、hybrid search、eval runner capability、API endpoint 或 frontend UI。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不 push tag 或建立 release note。

## Release Impact

- Target version: `v0.14.0`。
- Version bump required: no。
- 原因：本 ticket 只規劃 future demo / release checklist，不完成 runtime release；實際版本同步需等 future implementation ticket 明確要求。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md`

## Acceptance Criteria

- [ ] Future demo smoke preflight 順序已記錄。
- [ ] Future validation checklist 已記錄。
- [ ] Future release sync checklist 已記錄。
- [ ] 明確標示此 ticket 不執行 version bump 或 release sync。
- [ ] 明確標示 runtime implementation 需另開後續 ticket。

## Validation

- `rg -n "v0.14.0|demo smoke|release sync|Version bump required: no|future implementation" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-04-phase-14-demo-and-release-plan.md`
- `git diff --check`
