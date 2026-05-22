# 19-02 Sample Eval Coverage Expansion

## Goal

補齊面試 MVP 的公開虛構 sample data 與 retrieval eval dataset 覆蓋率，讓專案更接近 `goal.md` 的成功標準：至少 5 份 sample documents 與至少 20 筆 eval questions。

## Scope

- 新增或整理公開虛構 sample documents，使 `sample-data/documents/` 至少有 5 份可展示資料。
- 擴充 `sample-data/eval/retrieval-eval.json`，讓 retrieval eval cases 至少達到 20 筆。
- 新增 cases 應覆蓋 invoice、contract / support、cross-document ambiguity、numeric lookup、multi-evidence、lexical mismatch 與 demo-safe trace 說明。
- 更新 sample / eval README，說明資料皆為虛構、可公開、不可包含真實個資或公司敏感資料。
- 視需要更新 dataset contract tests，確保新增 cases 可被現有 smoke / pytest 驗證。

## Out of Scope

- 不新增真實資料、公司內部文件、個資、敏感資訊或外部下載資料。
- 不修改 retrieval algorithm、ranking policy、rerank provider、hybrid merge policy 或 smoke script behavior。
- 不實作 `hybrid_rerank` runtime、LLM-as-judge、answer faithfulness scoring、citation quality scoring 或 eval dashboard。
- 不新增 backend API、frontend UI、DB schema、Redis、NATS、worker 或 deployment 設定。

## Release Impact

- Target version: `v0.19.0` interview MVP packaging backlog。
- Version bump required: no。
- 原因：本 ticket 擴充 demo/eval fixtures，但 Phase 19 的完整 release sync 留到 `19-04`。

## Files likely to change

- `sample-data/documents/`
- `sample-data/eval/retrieval-eval.json`
- `sample-data/documents/README.md`
- `sample-data/eval/README.md`
- `backend/tests/test_eval_dataset.py`
- `TODO.md`
- `docs/ROADMAP.md`

## Acceptance Criteria

- [ ] `sample-data/documents/` 至少有 5 份公開虛構 sample documents。
- [ ] `sample-data/eval/retrieval-eval.json` 至少有 20 筆 eval cases。
- [ ] 新增 eval cases 都有 expected evidence，可由公開 sample documents 支撐。
- [ ] Baseline keyword eval smoke 仍可在無 Ollama embedding、Qdrant 或 FastEmbed runtime 時執行。
- [ ] 文件明確標示資料來源是 demo-safe synthetic content。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- `rg -n "case_count|20|sample documents|demo-safe|synthetic" sample-data docs/ROADMAP.md TODO.md`
- `git diff --check`
