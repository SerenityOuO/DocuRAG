# 15-02 Rerank Provider Adapter

## Goal

在 15-01 provider decision 完成後，新增 disabled-by-default 的 rerank provider adapter，讓 backend 可在明確設定後對 vector retrieval candidates 做 rerank。此 ticket 是程式 ticket，但不得讓 rerank 成為預設路徑。

## Scope

- 新增或更新 rerank provider 設定，例如 provider、model、top K、timeout 與 enabled flag。
- 實作最小 rerank adapter / service，輸入 query 與 retrieval candidates，輸出保留原 citation metadata 的 reranked candidates。
- 失敗時 fallback 到 rerank 前 candidates，並提供可讀的 fallback reason。
- 新增 backend unit tests，覆蓋 disabled path、success path、provider unavailable、timeout / malformed response 與 citation metadata preservation。
- 保持 keyword baseline 與 existing vector retrieval 行為不變。

## Out of Scope

- 不實作 hybrid search、BM25、score fusion 或 merge policy。
- 不修改 eval dataset JSON。
- 不新增 API endpoint、frontend UI、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不讓 rerank default-on。
- 不修改 demo smoke script 或 release/version files；release sync 留到 `15-04`。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。

## Release Impact

- Target version: `v0.15.0`。
- Version bump required: no。
- 原因：本 ticket 只新增 disabled-by-default rerank adapter building block；實際 `v0.15.0` release/version sync 留到 `15-04`。

## Files likely to change

- `.env.example`
- `backend/app/core/config.py`
- `backend/app/services/rerank.py`
- `backend/tests/test_rerank.py`
- `TODO.md`

## Acceptance Criteria

- [ ] Rerank provider 預設 disabled。
- [ ] Rerank adapter 可保留原 retrieval candidate 與 citation metadata。
- [ ] Rerank failure 會 fallback 到原 candidates，且記錄 fallback reason。
- [ ] Backend tests 覆蓋 success、disabled 與 failure paths。
- [ ] Keyword baseline 與 existing vector retrieval 預設行為不變。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `git diff --check`

