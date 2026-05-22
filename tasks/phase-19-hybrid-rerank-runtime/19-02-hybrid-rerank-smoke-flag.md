# 19-02 Hybrid Rerank Smoke Flag

## Goal

把 `hybrid_rerank` 接進本機 retrieval eval CLI 與 smoke script，新增 explicit optional smoke flag，讓 demo / validation 可以重跑 `hybrid_rerank` metrics 與 fallback metadata。

## Scope

- 更新 eval runner CLI strategy choices，支援 `hybrid_rerank`。
- 更新 `scripts/retrieval-eval-smoke.ps1`，新增 explicit `-RunHybridRerank` flag。
- Optional flag 必須與 `-RunVector`、`-RunVectorRerank`、`-RunHybrid` 互斥。
- `-RunHybridRerank` 應沿用 vector preflight、manual indexing preflight 與 rerank fallback behavior。
- 輸出 `.tmp/retrieval-eval-result-hybrid-rerank.json`，並檢查 summary / trace metadata 欄位存在。
- 更新 backend README 或 sample eval README 的 usage，說明 `hybrid_rerank` 是 optional eval strategy，不代表 `/rag/query` 或 frontend chat 已支援。

## Out of Scope

- 不新增 frontend UI、production eval dashboard、backend API endpoint 或 live eval runner。
- 不新增 default-on `hybrid_rerank`，不改 baseline demo smoke。
- 不新增 BM25 dependency、query rewriting、LLM-as-judge、answer faithfulness scoring 或 citation quality scoring。
- 不新增 Redis、NATS、worker、DB schema、Auth、RBAC、Agent runtime、deployment 或 release tag。

## Release Impact

- Target version: `v0.19.0`。
- Version bump required: no。
- 原因：本 ticket 新增 optional smoke path，但完整 `v0.19.0` version sync 留到 `19-04`。

## Files likely to change

- `backend/app/services/evaluation.py`
- `scripts/retrieval-eval-smoke.ps1`
- `backend/README.md`
- `sample-data/eval/README.md`
- `backend/tests/test_evaluation.py`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] Eval runner CLI 可接受 `--strategy hybrid_rerank`。
- [ ] `scripts/retrieval-eval-smoke.ps1 -RunHybridRerank` 可執行 optional eval smoke。
- [ ] Smoke script 對 optional flags 保持互斥檢查。
- [ ] `hybrid_rerank` smoke 輸出 summary metrics、fallback count、trace metadata count 與 result strategy counts。
- [ ] README / sample eval docs 說明此策略只屬於 optional eval runner，不接 default `/rag/query`。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional：`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1 -RunHybridRerank`
- `rg -n "RunHybridRerank|hybrid_rerank|retrieval-eval-result-hybrid-rerank" scripts backend README.md sample-data/eval/README.md TODO.md docs/ROADMAP.md`
- `git diff --check`
