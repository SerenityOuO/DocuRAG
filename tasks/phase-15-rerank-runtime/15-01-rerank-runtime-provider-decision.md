# 15-01 Rerank Runtime Provider Decision

## Goal

根據 Phase 14 的 rerank decision criteria，選定 Phase 15 / `v0.15.0` 的 rerank runtime provider 與模型候選，並明確記錄 dependency、model download、fallback 與 validation 風險。此 ticket 是文件與決策票，不新增 runtime。

## Scope

- 回顧 Phase 14 的 local-first、disabled-by-default、fallback-safe decision criteria。
- 比較 local reranker provider 候選，記錄模型大小、安裝方式、CPU/GPU 需求、授權與離線可用性。
- 決定 Phase 15 是否先做 `vector_rerank`，並確認 hybrid search 延後。
- 明確列出後續 implementation ticket 是否需要新增外部依賴、模型下載或 env setting。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 15 backlog。

## Out of Scope

- 不新增或修改 backend / frontend 程式碼。
- 不新增外部依賴、模型下載、Docker service 或 runtime provider。
- 不實作 rerank、hybrid search、BM25、score fusion 或 ranking pipeline。
- 不新增 eval dataset JSON、API endpoint、frontend UI、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。

## Release Impact

- Target version: `v0.15.0`。
- Version bump required: no。
- 原因：本 ticket 只決定 rerank runtime provider 與後續 implementation 邊界，不完成 runtime release，也不改變產品行為。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md`

## Acceptance Criteria

- [ ] Rerank provider candidates 已比較。
- [ ] Provider / model 選擇理由已記錄。
- [ ] 依賴、模型下載與 env setting 風險已記錄。
- [ ] 明確標示 Phase 15 先做 `vector_rerank`，hybrid search 延後。
- [ ] 明確標示此 ticket 不新增 runtime 或 version bump。

## Validation

- `rg -n "v0.15.0|Phase 15|rerank provider|vector_rerank|hybrid" TODO.md docs/ROADMAP.md tasks/phase-15-rerank-runtime/15-01-rerank-runtime-provider-decision.md`
- `git diff --check`

