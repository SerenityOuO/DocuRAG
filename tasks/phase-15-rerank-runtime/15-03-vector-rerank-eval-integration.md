# 15-03 Vector Rerank Eval Integration

## Goal

在 15-02 rerank provider adapter 完成後，將 disabled-by-default 的 `vector_rerank` strategy 接入 retrieval evaluation runner，讓 Phase 13 metrics 可以比較 `vector` 與 `vector_rerank`。此 ticket 不實作 hybrid search。

## Scope

- 新增 `vector_rerank` strategy label 到 eval runner 或 strategy selection。
- 讓 eval runner 在明確 env / flag 啟用時，先執行 vector retrieval，再對 candidates 套用 rerank adapter。
- 在 eval output 中記錄 rerank trace metadata，例如 strategy label、rerank enabled、provider、model、input candidate count、rerank top K、latency 與 fallback reason。
- 保留 baseline keyword eval 與 optional vector eval 的既有輸出格式。
- 新增 backend tests，覆蓋 `vector_rerank` success、reranker fallback 與 vector unavailable fallback。

## Out of Scope

- 不實作 hybrid search、BM25、score fusion 或 branch merge / dedupe。
- 不新增 eval dataset JSON 或 sample documents。
- 不新增 frontend UI、API endpoint、Redis、NATS、worker、async queue 或 PostgreSQL schema。
- 不修改 release/version files；release sync 留到 `15-04`。
- 不讓 `vector_rerank` default-on。
- 不新增登入、RBAC、VLM parser、PDF rendering 或 production OCR pipeline。

## Release Impact

- Target version: `v0.15.0`。
- Version bump required: no。
- 原因：本 ticket 只將 optional `vector_rerank` 接入 eval comparison；實際 release/version sync 留到 `15-04`。

## Files likely to change

- `backend/app/services/evaluation.py`
- `backend/tests/test_evaluation.py`
- `scripts/retrieval-eval-smoke.ps1`
- `TODO.md`

## Acceptance Criteria

- [ ] `vector_rerank` 只能由明確 env / flag 啟用。
- [ ] Eval output 保留 Phase 13 metrics，並新增 rerank trace metadata。
- [ ] Reranker failure 不會中斷 baseline eval。
- [ ] Existing keyword baseline eval 不需 external runtime 仍可執行。
- [ ] Backend tests 覆蓋 success 與 fallback paths。

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-backend.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-eval-smoke.ps1`
- Optional rerank eval smoke command must be documented by the implementation ticket.
- `git diff --check`

