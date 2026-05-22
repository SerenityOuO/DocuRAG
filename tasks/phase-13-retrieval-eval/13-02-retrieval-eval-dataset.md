# 13-02 Retrieval Evaluation Dataset

## Goal

新增最小公開 retrieval eval dataset，讓 Phase 13 後續 runner 可以用固定 query set 驗證 keyword / vector retrieval 的 hit rate、MRR 與 recall。Dataset 必須使用既有公開虛構 sample documents，不包含真實個資或公司敏感資料。

## Scope

- 新增或更新 `sample-data/eval/` 下的 retrieval eval dataset。
- Dataset 至少涵蓋 invoice 與 contract / support 兩類既有 sample content。
- 每筆 eval case 包含 query、top_k、expected document filename 或 id strategy、expected chunk hints、expected terms 與 tags。
- 補充 dataset README，說明資料來源、非敏感性、欄位意義與如何被 runner 使用。
- 新增 schema / loader 的最小測試或文件驗證，避免 dataset 格式漂移。
- 更新 `TODO.md` 中對應 checklist。

## Out of Scope

- 不新增 eval runner 執行策略比較。
- 不新增 API endpoint 或 frontend UI。
- 不新增 rerank、hybrid search 或 ranking model。
- 不新增新的真實文件、私有資料或大型資料集。
- 不新增 Redis、NATS、worker、PostgreSQL schema、登入或 RBAC。
- 不改 `/rag/query`、upload、OCR、manual vector indexing 的預設行為。

## Release Impact

- Target version: `v0.13.0`。
- Version bump required: no。
- 原因：此 ticket 只新增 eval dataset building block，不完成 Phase 13 release；版本同步留到 `13-04`。

## Files likely to change

- `sample-data/eval/README.md`
- `sample-data/eval/retrieval-eval.json`
- `backend/tests/test_eval_dataset.py`
- `TODO.md`

## Acceptance Criteria

- [ ] Retrieval eval dataset 使用公開虛構 sample data。
- [ ] 每筆 eval case 有 query、top_k、expected evidence 與 tags。
- [ ] Dataset schema 有最小測試或文件驗證。
- [ ] 不新增 runtime API 或改 `/rag/query` 預設行為。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `git diff --check`
