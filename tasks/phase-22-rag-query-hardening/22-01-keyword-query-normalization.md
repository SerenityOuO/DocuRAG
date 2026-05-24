# 22-01 Keyword Query Normalization

## Goal

改善 `/rag/query` 預設 keyword baseline 對中文查詢與常見 demo 問法的命中能力，讓「付款期限是什麼？」這類中文 query 可以命中既有英文 OCR chunks，並讓 LLM generation 在有 retrieved chunks 時取得上下文。

## Scope

- 強化 `KeywordRagProvider` 的 query / chunk tokenization，保留原本英文與數字 token 行為。
- 支援 CJK bigram token，讓中文 query 可命中中文 OCR chunks。
- 加入小範圍 demo-safe alias，將常見中文問法對應到既有 sample data 的英文 keyword，例如付款期限、付款條件、總金額、發票號碼、續約日期與 SLA 回覆目標。
- 補 backend tests，驗證中文 query 可命中英文 payment terms chunk，且 LLM provider 只在命中 retrieved chunks 後收到 prompt。
- 同步 `v0.22.0` release/version docs。

## Out of Scope

- 不新增 embedding、Qdrant、BM25、rerank、hybrid retrieval 或 `hybrid_rerank` default chat path。
- 不新增 query rewrite LLM call、LLM-as-judge、answer faithfulness scoring 或 citation quality scoring。
- 不修改 frontend route、backend API contract、資料庫 schema、auth、RBAC、Redis、NATS、worker、PDF rendering、image preprocessing 或 production OCR pipeline。
- 不改 sample data 與 retrieval eval dataset。

## Release Impact

- Target version: `v0.22.0`
- Version bump required: yes
- 原因：本 ticket 改變 default `/rag/query` keyword retrieval 行為，讓中文 query 與常見 alias 可在不啟用 vector runtime 的情況下命中 demo chunks。

## Files likely to change

- `backend/app/services/rag.py`
- `backend/tests/test_rag.py`
- `backend/app/core/config.py`
- `backend/tests/test_health.py`
- `backend/pyproject.toml`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/App.vue`
- `infra/docker-compose.yml`
- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [x] 中文 query `付款期限是什麼？` 能透過 keyword baseline 命中包含 `Payment terms: Net 15` 的英文 OCR chunk。
- [x] 有中文 alias 命中 retrieved chunks 時，既有 LLM generation path 可收到 query + retrieved chunks prompt。
- [x] 既有英文 keyword scoring、citations 與 retrieved chunks contract 不被破壞。
- [x] 文件明確說明這是 keyword normalization hardening，不是 default-on vector / hybrid / rerank。
- [x] Frontend 與 release 文件不宣稱 backend 已有正式知識庫 ingestion / indexing pipeline。
- [x] `v0.22.0` 版本與 release docs 同步完成。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `npm.cmd run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo-smoke-test.ps1`
- `rg -n "v0.22.0|Phase 22|keyword query normalization|付款期限|QUERY_ALIASES" README.md backend/README.md frontend/README.md TODO.md docs/ROADMAP.md backend/app backend/tests tasks/phase-22-rag-query-hardening/22-01-keyword-query-normalization.md`
- `git diff --check`
