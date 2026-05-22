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

## Decision Notes

### Phase 13 retrieval baseline input

Phase 13 已建立可重跑的 keyword baseline 與 optional vector eval smoke，作為 Phase 14 retrieval quality planning 的輸入：

- Keyword baseline：Hit Rate@K `0.8333`、MRR@K `0.6389`、Recall@K `0.75`、failure count `0`。
- Optional vector retrieval：Hit Rate@K `0.6667`、MRR@K `0.6667`、Recall@K `0.5833`、failure count `0`。

目前 keyword baseline 在 Hit Rate 與 Recall 較穩定；optional vector retrieval 的 MRR 略高，但 Hit Rate 與 Recall 較低。Phase 14 後續若要改善 retrieval quality，應先把 rerank 規劃成 optional、disabled-by-default 的品質層，用相同 eval runner 比較 `vector` 與 future `vector_rerank`，避免影響現有 keyword baseline。

### Rerank provider decision criteria

後續 implementation ticket 若要導入 rerank provider，需同時符合以下條件：

- Local-first 或 self-hosted 優先，不把外部 API 變成預設路徑。
- Disabled-by-default，必須由明確 env / provider setting 啟用。
- 失敗時可 fallback 到原 retrieval results，且不改變 keyword baseline 行為。
- 可使用 Phase 13 eval runner 做同 dataset、同 metrics 的可重跑比較。
- Trace metadata 必須能記錄 provider、model、input candidate count、rerank top K、rerank score、latency 與 fallback reason。
- 不要求新增 PostgreSQL schema、Redis、NATS、worker、async queue 或 frontend UI。
- 模型下載、外部依賴與 Docker runtime 必須由後續 ticket 明確要求後才可加入。

### Recommended sequencing

建議先規劃 `vector_rerank`，因為 Phase 12 / Phase 13 已有 optional vector retrieval 與 eval runner，可直接比較 vector candidates rerank 前後的 Hit Rate / MRR / Recall。`hybrid` 與 `hybrid_rerank` 應延後到 retrieval quality contract 固定 merge policy、dedupe rule 與 trace metadata 後再實作，避免在同一張 ticket 同時引入 keyword / vector merge 與 rerank 排序兩個變因。

本 ticket 不新增 runtime；Phase 14 只留下決策、排序建議與 guardrails，真正 rerank / hybrid implementation 必須另開後續 ticket。

## Acceptance Criteria

- [x] Phase 13 retrieval baseline metrics 已被引用為 Phase 14 decision input。
- [x] Rerank provider decision criteria 已記錄。
- [x] Hybrid search 是否延後、並如何與 rerank 比較，已有明確文字說明。
- [x] Phase 14 guardrails 已記錄，且沒有擴張到 code implementation。
- [x] `TODO.md` 與 `docs/ROADMAP.md` 已更新 Phase 14 backlog。

## Validation

- `rg -n "v0.14.0|Phase 14|rerank|hybrid|retrieval quality" TODO.md docs/ROADMAP.md tasks/phase-14-retrieval-quality/14-01-rerank-provider-decision.md`
- `git diff --check`
