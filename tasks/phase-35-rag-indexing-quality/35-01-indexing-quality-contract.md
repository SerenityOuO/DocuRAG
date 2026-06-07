# Indexing Quality Contract

## Goal

定義 Phase 35 RAG indexing quality contract，將 chunking、Qdrant payload index、metadata filter、reindex 與 stale vector cleanup 的範圍固定。

## Scope

- 定義 chunking strategy contract：fixed-size、semantic、parent-child。
- 定義 Qdrant payload metadata：tenant / project / document / source / page / chunk type。
- 定義 reindex document、reindex project、stale vector cleanup 與 indexing audit metadata。
- 更新 docs、TODO、ROADMAP 與 README_DEV。

## Out of Scope

- 不新增 runtime chunking strategy 或 Qdrant index code。
- 不新增 production eval dashboard、LLM-as-judge、answer scoring 或 citation quality scoring。
- 不修改 OCR、parser、Agent planner 或 Auth / RBAC 行為。

## Release Impact

- Target version: `none`
- Version bump required: no
- 原因：這是 Phase 35 contract ticket，不改 runtime。

## Files likely to change

- `docs/architecture.md`
- `docs/api.md`
- `docs/ROADMAP.md`
- `README_DEV.md`
- `TODO.md`
- `tasks/phase-35-rag-indexing-quality/35-01-indexing-quality-contract.md`

## Acceptance Criteria

- [x] 文件明確定義 three chunking strategies 與適用情境。
- [x] Qdrant payload metadata 與 filter contract 包含 tenant / project / document boundary。
- [x] Reindex 與 stale vector cleanup contract 清楚。
- [x] 明確標示本 ticket 不實作 runtime。

## Validation

- `rg -n "chunking|semantic|parent-child|Qdrant payload|reindex|stale vector|Phase 35" docs README_DEV.md TODO.md tasks/phase-35-rag-indexing-quality`
- `git diff --check`

## Validation Result

- Passed: `rg -n "chunking|semantic|parent-child|Qdrant payload|reindex|stale vector|Phase 35" docs README_DEV.md TODO.md tasks/phase-35-rag-indexing-quality`
- Passed: `git diff --check`（僅 Windows LF/CRLF 提示）
