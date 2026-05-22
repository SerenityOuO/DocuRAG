# 14-01 Rerank Provider Decision

## Goal

固定 Phase 14 / `v0.14.0` 的 retrieval quality planning boundary，根據 Phase 13 retrieval evaluation baseline 決定後續是否先規劃 rerank，並保留 hybrid search 的比較入口。此 ticket 是文件與決策票，不新增 runtime。

## Scope

- 回顧 Phase 13 keyword 與 optional vector eval metrics，記錄目前 retrieval quality baseline。
- 定義 rerank provider decision 的候選條件，例如 local-first、disabled-by-default、可用 eval runner 比較、失敗可 fallback。
- 規劃 rerank 與 hybrid search 的實作順序建議，但不實作任一策略。
- 明確記錄 Phase 14 guardrails，避免提前導入外部依賴、API、UI 或資料庫 schema。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 14 backlog。

## Out of Scope

- 不新增或修改 backend 程式碼。
- 不新增 rerank provider、reranker model client、hybrid search 或 ranking pipeline。
- 不新增 eval runner 功能、API endpoint 或 frontend UI。
- 不新增外部依賴、模型下載、Docker service、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。
- 不變更 keyword / vector retrieval 的預設行為。

## Release Impact

- Target version: `v0.14.0`。
- Version bump required: no。
- 原因：本 ticket 只建立 Phase 14 rerank decision 與 planning backlog，不完成 runtime release，也不改變產品行為。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md`

## Acceptance Criteria

- [ ] Phase 13 retrieval baseline metrics 已被引用為 Phase 14 decision input。
- [ ] Rerank provider decision criteria 已記錄。
- [ ] Hybrid search 是否延後、並如何與 rerank 比較，已有明確文字說明。
- [ ] Phase 14 guardrails 已記錄，且沒有擴張到 code implementation。
- [ ] `TODO.md` 與 `docs/ROADMAP.md` 已更新 Phase 14 backlog。

## Validation

- `rg -n "v0.14.0|Phase 14|rerank|hybrid|retrieval quality" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md`
- `git diff --check`
