# 12-01 Vector Indexing Contract

## Goal

固定 Phase 12 / `v0.12.0` 的 local vector indexing contract，讓後續 implementation ticket 有明確邊界。此 ticket 只做文件規劃，不新增 runtime。

## Scope

- 定義 Phase 12 的 vector indexing 目標與 release boundary。
- 固定 Qdrant point id、collection、vector size、payload metadata 與 indexing trace metadata contract。
- 定義 indexing failure / fallback 行為。
- 明確保留 keyword RAG baseline 與 optional Ollama `qwen3.5:4b` generation path。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 12 backlog。

## Out of Scope

- 不新增或修改 backend 程式碼。
- 不新增 indexing API。
- 不新增 persistent indexing runtime。
- 不實作 rerank、hybrid search 或 eval runner。
- 不新增 Redis、NATS、worker、PostgreSQL schema、登入或 RBAC。
- 不新增 VLM parser、PDF rendering 或 production OCR pipeline。
- 不讓 vector retrieval 成為 default-on path。

## Release Impact

- Target version: `v0.12.0`。
- Version bump required: no。
- 原因：本 ticket 只建立 Phase 12 contract 與 backlog，不完成 runtime release；版本同步留到 `12-04`。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md`

## Acceptance Criteria

- [ ] Phase 12 goal、scope 與 guardrails 已記錄。
- [ ] Qdrant point id 與 payload metadata contract 已記錄。
- [ ] Vector indexing failure / fallback 行為已記錄。
- [ ] Phase 12 backlog 已加入 `TODO.md` 與 `docs/ROADMAP.md`。
- [ ] 明確標示此 ticket 不 bump version。

## Validation

- `rg -n "v0.12.0|phase-12|Vector Indexing|docurag_chunks_v1" TODO.md docs/ROADMAP.md tasks/phase-12-vector-indexing/12-01-vector-indexing-contract.md`
- `git diff --check`
