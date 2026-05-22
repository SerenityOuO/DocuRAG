# 17-01 Retrieval Trace UI Contract

## Goal

固定 Phase 17 retrieval trace UI / eval visibility 的顯示 contract，讓後續 frontend 與 report work 可以一致呈現 keyword、vector、`vector_rerank` 與 `hybrid` metadata。此 ticket 是文件 ticket，只做 Markdown planning，不改 runtime。

## Scope

- 定義 frontend trace panel 應顯示的 retrieval strategy label、answer source、retrieval source、candidate count、latency 與 fallback state。
- 定義 candidate-level 顯示欄位，例如 rank、score、document id、chunk id、filename、source text preview 與 branch metadata。
- 規劃 `vector_rerank` metadata 顯示方式，包含 rerank provider、rerank status、rerank score 與 fallback reason。
- 規劃 `hybrid` metadata 顯示方式，包含 branch candidates、merge policy、dedupe count、branches、merged score 與 branch failures。
- 更新 `TODO.md` 與 `docs/ROADMAP.md` 的 Phase 17 planning 說明。

## Out of Scope

- 不修改 `backend/`、`frontend/`、`scripts/` 或 runtime code。
- 不新增 API endpoint、不改 `/rag/query` response schema、不接 eval runner 到 frontend。
- 不實作 production eval dashboard、LLM-as-judge、answer faithfulness、citation quality scoring 或 `hybrid_rerank`。
- 不新增外部依賴、Docker service、Redis、NATS、worker、async queue、PostgreSQL schema、登入、RBAC、VLM parser、PDF rendering、production OCR pipeline 或 deployment 設定。

## Files likely to change

- `TODO.md`
- `docs/ROADMAP.md`
- `tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md`

## Acceptance Criteria

- [ ] Trace UI contract 已涵蓋 keyword、vector、`vector_rerank` 與 `hybrid` strategy。
- [ ] Contract 已定義 run-level metadata、candidate-level metadata、fallback display 與 missing metadata 行為。
- [ ] 明確標示此 ticket 不修改 runtime、不新增 API、不新增 frontend implementation。
- [ ] `TODO.md` 與 `docs/ROADMAP.md` 已同步 Phase 17 planning 邊界。

## Validation

- `rg -n "v0.17.0|Phase 17|trace UI|hybrid|vector_rerank" TODO.md docs/ROADMAP.md tasks/phase-17-retrieval-trace-ui/17-01-retrieval-trace-ui-contract.md`
- `git diff --check`

## Release Impact

- Target version: `v0.17.0`。
- Version bump required: no。
- 原因：本 ticket 只固定 Phase 17 trace UI contract，不新增 runtime，也不形成 release artifact；實際版本同步留到 Phase 17 release ticket。
